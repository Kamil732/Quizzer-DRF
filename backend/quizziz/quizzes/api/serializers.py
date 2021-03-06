import random

from django.utils.translation import gettext as _
from rest_framework import serializers
from rest_framework.reverse import reverse
from rest_framework.response import Response

from quizziz.utils import valid_url_extension

from quizzes.models import (
    Quiz,
    QuizFeedback,
    QuizPunctation,
    Question,
    Category,
    PsychologyResults,
    Answer,
)


class ImageValidatorSerailizer(serializers.Serializer):
    image_url = serializers.CharField(allow_blank=True)
    success = serializers.BooleanField(default=False, read_only=True)

    def validate(self, data):
        image_url = data.get('image_url')

        if not(image_url.strip()):
            data['success'] = True
            data['image_url'] = Quiz.DEFAULT_IMAGE
        elif valid_url_extension(data['image_url']):
            data['success'] = True
        else:
            data['image_url'] = Quiz.DEFAULT_IMAGE

        return data

    class Meta:
        fields = ('image_url',)
        read_only_fields = ('success',)


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('name', 'display_name')


class AnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = (
            'image_url',
            'answer',
            'answered_times',
            'slug',
        )


class PsychologyResultUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = PsychologyResults
        fields = ('id', 'result',)


class AnswerUpdateSerializer(AnswerSerializer):
    results = PsychologyResultUpdateSerializer(many=True, read_only=True)

    def validate_points(self, value):
        if not(value):
            return '0'
        return value

    class Meta(AnswerSerializer.Meta):
        fields = (
            'id',
            'answer',
            'image_url',
            'points',
            'results',
        )


class QuestionSerializer(serializers.ModelSerializer):
    image_url = serializers.CharField(allow_blank=True)
    answers = serializers.SerializerMethodField('get_answers')

    def validate_image_url(self, value):
        if not(valid_url_extension(value)):
            return ''

        return value

    def get_answers(self, obj):
        answers = sorted(obj.answers.all(), key=lambda x: random.random())
        return AnswerSerializer(answers, many=True).data

    class Meta:
        model = Question
        fields = (
            'id',
            'question',
            'image_url',
            'summery',
            'answers',
        )
        read_only_fields = ('slug',)


class QuestionUpdateSerializer(QuestionSerializer):
    def get_answers(self, obj):
        answers = obj.answers.order_by('id')
        return AnswerUpdateSerializer(answers, many=True).data


class QuizSerializer(serializers.Serializer):
    is_published = serializers.BooleanField(default=True)
    author_slug = serializers.ReadOnlyField(source='author.slug')
    pub_date = serializers.SerializerMethodField('get_pub_date')
    max_score = serializers.SerializerMethodField('get_max_score')
    average_points = serializers.SerializerMethodField('get_average_points')
    image_url = serializers.CharField(allow_blank=True)
    category = serializers.CharField(max_length=50)
    section = serializers.CharField(max_length=50)
    question_amount = serializers.SerializerMethodField('get_question_amount')

    def get_pub_date(self, obj):
        return f'{obj.pub_date.day}-{obj.pub_date.month}-{obj.pub_date.year}'

    def get_question_amount(self, obj):
        return Question.objects.filter(quiz_id=obj.id).count()

    def get_max_score(self, obj):
        if obj.section == 'knowledge_quiz':
            return self.get_question_amount(obj)
        elif obj.section == 'universal_quiz':
            questions = Question.objects.filter(quiz__author__slug=obj.author.slug, quiz__slug=obj.slug)

            max_scores = []
            for question in questions:
                question_points = list(map(int, Answer.objects.filter(
                    question=question).values_list('points', flat=True)))

                max_scores.append(max(question_points))

            return sum(max_scores)
        return 0  # Default value

    def get_average_points(self, obj):
        try:
            return round(sum(obj.answers_data) / obj.solved_times, 2) if self.get_max_score(obj) > 0 else None
        except:
            return None

    def validate_category(self, value):
        return Category.objects.get(
            name=value)

    def validate_image_url(self, value):
        if not(value.strip()) or not(valid_url_extension(value)):
            return Quiz.DEFAULT_IMAGE

        return value

    def to_representation(self, instance):
        representation = super(QuizSerializer, self).to_representation(instance)

        representation['category'] = {
            'name': instance.category.name,
            'display_name': instance.category.display_name,
        }

        representation['section'] = {
            'name': instance.section,
            'display_name': instance.get_section_display(),
        }

        return representation


class QuizListSerializer(QuizSerializer, serializers.ModelSerializer):
    random_question_order = serializers.BooleanField(
        default=True, read_only=True)
    author = serializers.ReadOnlyField(source='author.username')

    class Meta:
        model = Quiz
        fields = (
            'pub_date',
            'is_published',
            'random_question_order',
            'image_url',
            'section',
            'category',
            'title',
            'description',
            'solved_times',
            'average_points',
            'max_score',
            'slug',
            'author',
            'author_slug',
            'category',
            'question_amount',
        )
        read_only_fields = ('slug', 'solved_times',)

    def create(self, data):
        quiz = Quiz.objects.create(**data)

        if data['section'] == 'psychology_quiz':
            PsychologyResults.objects.bulk_create(
                [PsychologyResults(quiz=quiz, result=f'You are {str(i + 1)}...', description=f'Not everyone is {str(i+ 1)}...') for i in range(4)])
        else:
            QuizPunctation.objects.create(quiz=quiz, from_score=0, to_score=0, result='Bravo!',
                                          description="That's the end of hard questions :)")

        return quiz


class QuizDetailSerializer(QuizSerializer, serializers.ModelSerializer):
    random_question_order = serializers.BooleanField(
        default=True)
    questions = serializers.SerializerMethodField('get_questions')
    author = serializers.SerializerMethodField('get_author')

    def get_author(self, obj):
        request = self.context.get('request')
        return request.build_absolute_uri(reverse('account', args=[obj.author.slug]))

    def get_questions(self, obj):
        request = self.context.get('request')
        return request.build_absolute_uri(reverse('quiz-question-list', args=[obj.author.slug, obj.slug]))

    class Meta:
        model = Quiz
        exclude = (
            'id',
            'answers_data',
        )
        read_only_fields = ('questions', 'author',)


class QuizPunctationSerializer(serializers.ModelSerializer):
    def vaildate(self, data):
        if (data['from_score'] > data['to_score']):
            raise serializers.ValidationError({'detail': _('From score cannot be greater than to score')})

        return data

    class Meta:
        model = QuizPunctation
        exclude = ('id', 'quiz', 'slug',)


class PsychologyResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = PsychologyResults
        exclude = ('quiz', 'slug',)


class QuizFeedbackSerializer(serializers.ModelSerializer):
    pub_date = serializers.SerializerMethodField('get_pub_date')

    def get_pub_date(self, obj):
        return f'{obj.pub_date.day}-{obj.pub_date.month}-{obj.pub_date.year}'

    def validate(self, data):
        quiz = self.context['quiz']

        if quiz['ask_name'] and not(data['name']):
            raise serializers.ValidationError({'name': _('Name cannot be blank')})
        if quiz['ask_email'] and not(data['email']):
            raise serializers.ValidationError({'email': _('Email cannot be blank')})
        if quiz['ask_gender'] and not(data['gender']):
            raise serializers.ValidationError({'gender': _('Gender cannot be blank')})

        return data

    class Meta:
        model = QuizFeedback
        exclude = ('quiz',)
