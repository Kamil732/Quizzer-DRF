import random

from django.utils.translation import gettext as _
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q

from bulk_sync import bulk_sync
from rest_framework import views, generics, viewsets, permissions
from rest_framework import status
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError, NotFound

from quizzes.models import Quiz, QuizFeedback, QuizPunctation, Section, Category, Question, PsychologyResults, Answer

from . import serializers, permissions, mixins


class ImageValidatorAPIView(generics.GenericAPIView):
    serializer_class = serializers.ImageValidatorSerailizer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        return Response(serializer.data, status=status.HTTP_200_OK)


class SectionViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = serializers.SectionSerializer
    queryset = Section.objects.all()
    lookup_field = 'name'


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = serializers.CategorySerializer
    queryset = Category.objects.all()
    lookup_field = 'name'


class QuestionUpdateListAPIView(mixins.QuestionMixin, generics.ListAPIView):
    serializer_class = serializers.QuestionUpdateSerializer


class QuestionListAPIView(mixins.QuestionMixin, generics.ListCreateAPIView):
    def perform_create(self, serializer):
        author_slug = self.kwargs.get('author_slug')
        quiz_slug = self.kwargs.get('quiz_slug')
        quiz_id = Quiz.objects.filter(
            author__slug=author_slug, slug=quiz_slug).values_list('id', flat=True).first()

        serializer.save(quiz_id=quiz_id)

    def get_queryset(self, *args, **kwargs):
        author_slug = self.kwargs.get('author_slug')
        quiz_slug = self.kwargs.get('quiz_slug')

        try:
            quiz = Quiz.objects.get(author__slug=author_slug, slug=quiz_slug)
        except ObjectDoesNotExist:
            raise NotFound(
                _('The quiz you are looking for does not exist'))

        if quiz.random_question_order:
            return sorted(Question.objects.filter(quiz=quiz), key=lambda x: random.random())
        return Question.objects.filter(quiz=quiz)


class QuestionDetailAPIView(mixins.QuestionMixin, generics.RetrieveUpdateDestroyAPIView):
    lookup_field = 'slug'
    lookup_url_kwarg = 'question_slug'


class AnswerListAPIView(mixins.AnswerMixin, generics.ListCreateAPIView):
    def perform_create(self, serializer):
        author_slug = self.kwargs.get('author_slug')
        quiz_slug = self.kwargs.get('quiz_slug')
        question_slug = self.kwargs.get('question_slug')
        question = Question.objects.get(quiz__author__slug=author_slug, quiz__slug=quiz_slug, slug=question_slug)

        serializer.save(question_id=question.id)


class AnswerDetailAPIView(mixins.AnswerMixin, generics.RetrieveUpdateDestroyAPIView):
    lookup_field = 'slug'
    lookup_url_kwarg = 'answer_slug'


class QuizDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Quiz.objects.order_by(
        '-pub_date', '-solved_times')
    permission_classes = (permissions.IsOwner,)
    serializer_class = serializers.QuizDetailSerializer

    def get_object(self, *args, **kwargs):
        author_slug = self.kwargs.get('author_slug')
        quiz_slug = self.kwargs.get('quiz_slug')

        try:
            return Quiz.objects.get(author__slug=author_slug, slug=quiz_slug)
        except ObjectDoesNotExist:
            raise NotFound(
                _('The quiz you are looking for does not exist'))


class QuizListAPIView(mixins.QuizListMixin, generics.ListCreateAPIView):
    queryset = Quiz.objects.order_by(
        '-pub_date', '-solved_times').filter(is_published=True)
    permission_classes = (permissions.CreateIsAuthenticated,)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class QuizUpdateAPIView(generics.UpdateAPIView):
    queryset = Quiz.objects.order_by(
        '-pub_date', '-solved_times')
    permission_classes = (permissions.IsOwner,)

    def update(self, request, *args, **kwargs):
        questions = request.data

        author_slug = self.kwargs.get('author_slug')
        quiz_slug = self.kwargs.get('quiz_slug')
        quiz = Quiz.objects.get(author__slug=author_slug, slug=quiz_slug)

        new_questions = [Question(quiz=quiz, question=question['question'], summery=question['summery'],
                                  image_url=question['image_url'], slug=str(index)) for (index, question) in enumerate(questions)]

        # TODO: Questions should NOT be unique
        # Check if question is unique
        for model in new_questions:
            if ([x.question for x in new_questions].count(model.question) > 1):
                raise ValidationError({'detail': _('There cannot be more than 1 question with the same text')})

        #### Save answers ####
        for (index, question) in enumerate(questions):
            if not(question['answers']) or len(question['answers']) < 2:
                raise ValidationError({'detail': _('Every question should have at least 2 answers')})
            elif len(question['answers']) > 8:
                raise ValidationError({'detail': _('Questions should have maxiumum 8 answers')})

            # Check if answer is unique
            for answer in question['answers']:
                if ([answer_['answer'] for answer_ in question['answers']].count(answer['answer']) > 1):
                    raise ValidationError({'detail': _('There cannot be more than 1 answer with the same text')})

            # If there is no error than save questions
            if index == 0:
                bulk_sync(
                    new_models=new_questions,
                    filters=Q(quiz_id=quiz.id),
                    fields=['question', 'summery', 'image_url'],
                    key_fields=('slug',)  # slug is index from enumerate
                )

            question_model = Question.objects.get(quiz=quiz, question=question['question'])

            new_answers = [
                Answer(
                    question=question_model,
                    answer=answer['answer'],
                    image_url=answer['image_url'],
                    is_correct=index_ == 0 if quiz.section.name == 'knowledge_quiz' else False,
                    points=answer['points'],
                    slug=str(index_))
                for (index_, answer) in enumerate(question['answers'])
            ]

            bulk_sync(
                new_models=new_answers,
                filters=Q(question_id=question_model.id),
                fields=['answer', 'image_url', 'is_correct', 'points'],
                key_fields=('slug',)  # slug is index from enumerate
            )

            if quiz.section.name == 'psychology_quiz':
                # Set results to each answer
                for answer_data in question['answers']:
                    # Get answer
                    answer = Answer.objects.get(question=question_model, answer=answer_data['answer'])

                    # Get results given to this answer in data
                    results = [PsychologyResults.objects.get(quiz=quiz, id=result['id'])
                               for result in answer_data['results']]

                    if results:
                        answer.results.set(results)
                    else:
                        # If there are no results than error should be thrown
                        raise ValidationError({'detail': _('Every answer have to have result to it')})

         #### Set punctations ####
        if quiz.section.name == 'knowledge_quiz' or quiz.section.name == 'universal_quiz':
            if quiz.section.name == 'knowledge_quiz':
                max_score = Question.objects.filter(quiz=quiz).count()
            else:
                questions = Question.objects.filter(quiz__author__slug=author_slug, quiz__slug=quiz_slug)

                max_scores = []
                for question in questions:
                    question_points = list(map(int, Answer.objects.filter(
                        question=question).values_list('points', flat=True)))

                    max_scores.append(max(question_points))

                max_score = sum(max_scores)

            punctations = list(QuizPunctation.objects.filter(quiz=quiz).order_by('id'))
            expectedFrom = 0

            for punctation in punctations:
                punctation.from_score = expectedFrom
                expectedTo = punctation.to_score

                if expectedTo < expectedFrom:
                    expectedTo = expectedFrom
                    punctation.to_score = expectedTo

                expectedFrom = expectedTo + 1
                if expectedFrom > max_score:
                    expectedFrom = max_score

            for punctation in punctations:
                punctation.save()

            expectedTo = max_score
            for punctation in punctations[::-1]:
                punctation.to_score = expectedTo
                expectedFrom = punctation.from_score

                if expectedFrom > expectedTo:
                    expectedFrom = expectedTo
                    punctation.from_score = expectedFrom

                expectedTo = expectedFrom - 1 if expectedFrom - 1 >= 0 else 0

            for punctation in punctations:
                punctation.save()

        return Response({'message': 'Successfully updated'})


class QuizFinishAPIView(views.APIView):
    def post(self, request, fromat=False, *args, **kwargs):
        author_slug = self.kwargs.get('author_slug')
        quiz_slug = self.kwargs.get('quiz_slug')
        section = request.data.get('section')

        # Psychology
        results = []

        retrieveData = {
            'summery': '',
            'points': 0,
            'data': [],
        }

        # Check if quiz exists
        try:
            quiz = Quiz.objects.get(author__slug=author_slug, slug=quiz_slug)
            # Add 1 to solved_times
            quiz.solved_times += 1
            quiz.save
        except ObjectDoesNotExist:
            raise NotFound(
                _('The quiz you are looking for does not exist'))

        for answer in request.data.get('data'):
            question_id = answer.get('questionId')
            answer_slug = answer.get('answer')

            if not(answer_slug):
                raise ValidationError(
                    _('You have not answered all the questions'))

            if section == 'knowledge_quiz':
                correct_answers = [answer_.get('slug') for answer_ in Answer.objects.filter(
                    question__id=question_id, is_correct=True).values('slug')]

                # Add 1 to points if it is correct answer
                retrieveData['points'] += 1 if answer_slug in correct_answers else 0
                retrieveData['data'].append({
                    'correct_answers': correct_answers,
                    'questionId': question_id,
                    'selected': answer_slug,
                })

            elif section == 'universal_quiz':
                points = int(Answer.objects.filter(question__id=question_id,
                                                   slug=answer_slug).values_list('points', flat=True).first())

                retrieveData['points'] += points
                retrieveData['data'].append({
                    'questionId': question_id,
                    'selected': answer_slug,
                })
            elif section == 'preferential_quiz':
                answer = Answer.objects.get(question__id=question_id, slug=answer_slug)
                answer.answered_times += 1
                answer.save()

                retrieveData['data'].append({
                    'questionId': question_id,
                    'selected': answer_slug,
                })

            elif section == 'psychology_quiz':
                answer = Answer.objects.get(question__id=question_id, slug=answer_slug)
                results.append(answer.results.values_list('id', flat=True))

                retrieveData['data'].append({
                    'questionId': question_id,
                    'selected': answer_slug,
                })

        if section == 'knowledge_quiz' or section == 'universal_quiz':
            quiz.answers_data.append(retrieveData['points'])
            quiz.save()

            summery = QuizPunctation.objects.filter(
                quiz=quiz, from_score__lte=retrieveData['points'], to_score__gte=retrieveData['points']).values_list('result', 'description').first()

        elif section == 'preferential_quiz':
            summery = QuizPunctation.objects.filter(quiz=quiz).values_list('result', 'description').first()

        elif section == 'psychology_quiz':
            results = [x for result in results for x in result]
            most_occur_result_id = max(results, key=results.count)

            summery = PsychologyResults.objects.filter(
                id=most_occur_result_id).values_list('result', 'description').first()

        retrieveData['summery'] = summery

        return Response(retrieveData, status=status.HTTP_200_OK)


class QuizPunctationListAPIView(generics.ListCreateAPIView, generics.UpdateAPIView):
    permission_classes = (permissions.IsOwnerEverything,)

    def get_serializer_class(self):
        author_slug = self.kwargs.get('author_slug')
        quiz_slug = self.kwargs.get('quiz_slug')

        section = Quiz.objects.filter(author__slug=author_slug, slug=quiz_slug).values_list(
            'section__name', flat=True).first()

        if not(section == 'psychology_quiz'):
            return serializers.QuizPunctationSerializer
        return serializers.PsychologyResultSerializer

    def get_queryset(self):
        author_slug = self.kwargs.get('author_slug')
        quiz_slug = self.kwargs.get('quiz_slug')

        section = Quiz.objects.filter(author__slug=author_slug, slug=quiz_slug).values_list(
            'section__name', flat=True).first()

        if not(section == 'psychology_quiz'):
            return QuizPunctation.objects.filter(quiz__author__slug=author_slug, quiz__slug=quiz_slug).order_by('id')
        return PsychologyResults.objects.filter(quiz__author__slug=author_slug, quiz__slug=quiz_slug).order_by('id')

    def perform_create(self, serializer):
        author_slug = self.kwargs.get('author_slug')
        quiz_slug = self.kwargs.get('quiz_slug')
        quiz = Quiz.objects.get(author__slug=author_slug, slug=quiz_slug)

        serializer.save(quiz_id=quiz.id)

    def update(self, request, *args, **kwargs):
        author_slug = self.kwargs.get('author_slug')
        quiz_slug = self.kwargs.get('quiz_slug')

        section = Quiz.objects.filter(author__slug=author_slug, slug=quiz_slug).values_list(
            'section__name', flat=True).first()
        quiz = Quiz.objects.get(author__slug=author_slug, slug=quiz_slug)

        new_models = [QuizPunctation(quiz=quiz, result=model['result'], description=model['description'], from_score=model['from_score'],
                                     to_score=model['to_score'], slug=str(index)) for (index, model) in enumerate(request.data)] if not(section == 'psychology_quiz') else [PsychologyResults(quiz=quiz, result=model['result'],
                                                                                                                                                                                              description=model['description'], slug=str(index)) for (index, model) in enumerate(request.data)]

        # Check if result is unique
        for model in new_models:
            if ([x.result for x in new_models].count(model.result) > 1):
                raise ValidationError({'detail': _('There cannot be more than 1 result with the same text')})

        fields = ['result', 'description', 'from_score', 'to_score'] if not(
            section == 'psychology_quiz') else ['result', 'description']

        bulk_sync(
            new_models=new_models,
            filters=Q(quiz_id=quiz.id),
            fields=fields,
            key_fields=('slug',)  # slug is index from enumerate
        )

        if section == 'psychology_quiz':
            questions = Question.objects.filter(quiz_id=quiz.id).prefetch_related('answers')

            # Check if there are some new created punctations
            # If there are then we need to add them to the first answer as default
            for question in questions:
                # Get the first answer
                first_answer = question.answers.prefetch_related('results').first()

                # The punctations from given data
                punctations = [model['result'] for model in request.data]

                # All the results from all answers
                results = []

                # Result that we need to add to the first answer
                new_results = []

                # Add all the results from all answers
                for answer in question.answers.prefetch_related('results').all():
                    for result in [result.result for result in answer.results.all()]:
                        results.append(result)

                # Add all the results that are new created to new_results
                for punctation in punctations:
                    if not(punctation in results):
                        new_results.append(PsychologyResults.objects.get(quiz=quiz, result=punctation))

                # Add all new_results to first answer
                for result in new_results:
                    first_answer.results.add(result)

        return Response(request.data, status=status.HTTP_200_OK)


class QuizFeedbacksAPIView(generics.ListCreateAPIView):
    serializer_class = serializers.QuizFeedbackSerializer
    permission_classes = (permissions.GetIsOwner,)

    def get_queryset(self):
        author_slug = self.kwargs.get('author_slug')
        quiz_slug = self.kwargs.get('quiz_slug')

        try:
            quiz = QuizFeedback.objects.filter(quiz__author__slug=author_slug, quiz__slug=quiz_slug)
        except ObjectDoesNotExist:
            raise NotFound(
                _('The quiz you are looking for does not exist'))

        return quiz

    def get_serializer_context(self):
        author_slug = self.kwargs.get('author_slug')
        quiz_slug = self.kwargs.get('quiz_slug')
        quiz = Quiz.objects.filter(author__slug=author_slug, slug=quiz_slug).values(
            'ask_name', 'ask_email', 'ask_gender').first()

        return {
            'quiz': quiz,
            'request': self.request,
        }

    def perform_create(self, serializer):
        author_slug = self.kwargs.get('author_slug')
        quiz_slug = self.kwargs.get('quiz_slug')
        quiz = Quiz.objects.get(author__slug=author_slug, slug=quiz_slug)

        serializer.save(quiz_id=quiz.id)


class DeleteQuizFeedbackAPIView(generics.DestroyAPIView):
    lookup_field = 'id'
    lookup_url_kwarg = 'feedback_id'

    def get_queryset(self):
        author_slug = self.kwargs.get('author_slug')
        quiz_slug = self.kwargs.get('quiz_slug')

        return QuizFeedback.objects.filter(quiz__author__slug=author_slug, quiz__slug=quiz_slug)
