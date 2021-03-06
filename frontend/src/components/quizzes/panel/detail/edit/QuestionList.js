import React, { Component } from 'react'
import PropTypes from 'prop-types'

import Textarea from '../../../../Textarea'
import ImageUrlPreview from '../../../ImageUrlPreview'

import { RiImageEditFill, RiQuestionnaireFill } from 'react-icons/ri'
import KnowledgeAnswers from './answers/KnowledgeAnswers'
import PsychologyAnswers from './answers/PsychologyAnswers'
import PreferentialAnswers from './answers/PreferentialAnswers'
import UniversalAnswers from './answers/UniversalAnswers'
import { connect } from 'react-redux'

class QuestionList extends Component {
	static propTypes = {
		initialQuestions: PropTypes.array,
		questions: PropTypes.array,
		punctations: PropTypes.array,
		section_name: PropTypes.string.isRequired,
		removeQuestion: PropTypes.func.isRequired,
		hasChanged: PropTypes.func.isRequired,
		setQuestions: PropTypes.func.isRequired,
	}

	constructor(props) {
		super(props)

		this.onChange = this.onChange.bind(this)
	}

	onChange = (e) => {
		const { setQuestions } = this.props
		let questions = this.props.questions

		questions = questions.map((question, index) => {
			if (index === parseInt(e.target.getAttribute('data-id'))) {
				return {
					...question,
					[e.target.name]: e.target.value,
				}
			}
			return question
		})

		setQuestions(questions)
	}

	componentDidUpdate(prevProps, _) {
		// Check if form has changed
		if (
			JSON.stringify(prevProps.questions) !==
			JSON.stringify(this.props.questions)
		) {
			const { hasChanged, initialQuestions, questions } = this.props

			if (initialQuestions.length !== questions.length) {
				hasChanged(true)
				return
			}

			if (
				hasChanged &&
				initialQuestions.length > 0 &&
				questions.length > 0
			) {
				// Check if questions has changed
				const questions1 = initialQuestions.map((question) => ({
					question: question.question,
					summery: question.summery,
					image_url: question.image_url,
				}))

				const questions2 = questions.map((question) => ({
					question: question.question,
					summery: question.summery,
					image_url: question.image_url,
				}))

				// Check if answers has changed
				const answers1 = initialQuestions.map((question) => ({
					...question.answers,
				}))

				const answers2 = questions.map((question) => ({
					...question.answers,
				}))

				hasChanged(
					JSON.stringify(questions1) !== JSON.stringify(questions2) ||
						JSON.stringify(answers1) !== JSON.stringify(answers2)
				)
			}
		}
	}

	render() {
		const {
			questions,
			initialQuestions,
			removeQuestion,
			hasChanged,
			setQuestions,
			section_name,
			punctations,
		} = this.props

		const questionList = questions.map((question, index) => {
			let answers

			const initialAnswers = initialQuestions[index]
				? initialQuestions[index].answers.map((answer) => ({
						...answer,
				  }))
				: []

			if (section_name === 'knowledge_quiz')
				answers = (
					<KnowledgeAnswers
						initialAnswers={initialAnswers}
						answers={question.answers}
						questions={questions}
						questionIndex={index}
						hasChanged={hasChanged}
						setQuestions={setQuestions}
					/>
				)
			else if (section_name === 'universal_quiz')
				answers = (
					<UniversalAnswers
						initialAnswers={initialAnswers}
						answers={question.answers}
						questions={questions}
						questionIndex={index}
						hasChanged={hasChanged}
						setQuestions={setQuestions}
					/>
				)
			else if (section_name === 'preferential_quiz')
				answers = (
					<PreferentialAnswers
						initialAnswers={initialAnswers}
						answers={question.answers}
						questions={questions}
						questionIndex={index}
						hasChanged={hasChanged}
						setQuestions={setQuestions}
					/>
				)
			else if (section_name === 'psychology_quiz')
				answers = (
					<PsychologyAnswers
						initialAnswers={initialAnswers}
						answers={question.answers}
						punctations={punctations}
						section_name={section_name}
						questions={questions}
						questionIndex={index}
						hasChanged={hasChanged}
						setQuestions={setQuestions}
					/>
				)

			return (
				<div className="card" key={index}>
					<div className="card__body">
						<div className="row">
							<div className="col-md-7">
								<div className="form-control">
									<label className="form-control__label">
										Question:
									</label>
									<div className="icon-form">
										<span className="icon">
											<RiQuestionnaireFill />
										</span>

										<input
											type="text"
											data-id={index}
											onChange={this.onChange}
											name="question"
											value={
												this.props.questions[index]
													.question
											}
											className="form-control__input form-control__textarea"
											placeholder="Pass the question..."
											maxLength="100"
										/>
									</div>
								</div>

								{answers}

								<div className="form-control">
									<label className="form-control__label">
										Summery:
									</label>
									<Textarea
										data-id={index}
										onChange={this.onChange}
										name="summery"
										value={
											this.props.questions[index].summery
										}
										className="form-control__input form-control__textarea"
										placeholder="Pass the summery..."
										rows="3"
									/>
								</div>
							</div>
							<div className="col-md-5">
								<div className="form-control">
									<label className="form-control__label">
										Image Url:
									</label>
									<div className="icon-form">
										<span className="icon">
											<RiImageEditFill />
										</span>

										<input
											type="text"
											data-id={index}
											onChange={this.onChange}
											name="image_url"
											value={
												this.props.questions[index]
													.image_url
											}
											className="form-control__input form-control__textarea"
											placeholder="Pass the image url..."
											rows="3"
										/>
									</div>
								</div>
								<ImageUrlPreview
									image_url={
										this.props.questions[index].image_url
											.length > 0
											? this.props.questions[index]
													.image_url
											: 'https://static.thenounproject.com/png/2999524-200.png'
									}
									defaultImage="https://static.thenounproject.com/png/2999524-200.png"
								/>
							</div>
						</div>
					</div>
					<div className="card__footer">
						<button
							type="button"
							className={`btn btn__danger ${
								questions.length === 1 ? 'btn__disabled' : ''
							}`}
							style={{
								margin: '0 auto',
							}}
							onClick={() => removeQuestion(index)}
						>
							Delete Question
						</button>
					</div>
				</div>
			)
		})

		return questionList
	}
}

const mapStateToProps = (state) => ({
	punctations: state.quizzes.quizzes.item.punctations,
})

export default connect(mapStateToProps)(QuestionList)
