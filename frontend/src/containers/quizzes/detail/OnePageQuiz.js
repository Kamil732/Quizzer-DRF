import React, { Component } from 'react'
import PropTypes from 'prop-types'
import KnowledgeAnswers from './answers/KnowledgeAnswers'
import PsychologyAnswers from './answers/PsychologyAnswers'
import PreferentailAnswers from './answers/PreferentailAnswers'
import UniversalAnswers from './answers/UniversalAnswers'

class OnePageQuiz extends Component {
    static propTypes = {
        questions: PropTypes.array,
        section: PropTypes.string.isRequired,
    }

    render() {
        const { questions, section } = this.props

        const questionList = questions.map((question, index) => {
            let answers

            if (section === 'knowledge_quiz')
                answers = <KnowledgeAnswers
                    answers={question.answers}
                    questionId={question.id}
                />
            else if (section === 'psychology_quiz')
                answers = <PsychologyAnswers
                    answers={question.answers}
                    questionId={question.id}
                />
            else if (section === 'preferential_quiz')
                answers = <PreferentailAnswers
                    answers={question.answers}
                    questionId={question.id}
                />
            else if (section === 'universal_quiz')
                answers = <UniversalAnswers
                    answers={question.answers}
                    questionId={question.id}
                />

            return (
                <div className="card" key={index}>
                    <div className="card__header">{question.question}</div>
                    <div className="card__body">
                        <div className="answer-container">
                            {answers}
                        </div>
                    </div>
                </div>
            )
        })

        return questionList
    }
}

export default OnePageQuiz
