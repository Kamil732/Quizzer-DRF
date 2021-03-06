import React, { Component } from 'react'
import PropTypes from 'prop-types'
import Title from '../../../common/Title'

import axios from 'axios'

import CircleLoader from '../../../components/loaders/CircleLoader'
import OnePageQuiz from './OnePageQuiz'
import MultiPageQuiz from './MultiPageQuiz'
import FeedbackForm from '../../../components/quizzes/panel/detail/FeedbackForm'
import Ad from '../../../components/Ad'

class Start extends Component {
	static propTypes = {
		author_slug: PropTypes.string.isRequired,
		isOwner: PropTypes.bool,
		data: PropTypes.object.isRequired,
	}

	constructor(props) {
		super(props)

		const { ask_name, ask_email, ask_gender, ask_opinion } = props.data

		this.state = {
			loading: true,
			questions: [],
			timer: 0,
			finished_data: {},
			sentFeedback:
				!ask_name && !ask_email && !ask_gender && !ask_opinion,

			password: '',
			correctPassword: false,
			passwordError: '',
		}

		this.getQuestions = this.getQuestions.bind(this)
		this.onChangePassword = this.onChangePassword.bind(this)
		this.onSubmit = this.onSubmit.bind(this)
	}

	getQuestions = () => {
		this.setState({ loading: true })
		const { data } = this.props

		axios
			.get(data.questions)
			.then((res) => {
				this.setState({
					loading: false,
					questions: res.data,
				})

				this.timer = setInterval(
					() =>
						this.setState((prevState) => ({
							timer: prevState.timer + 1,
						})),
					1000
				)
			})
			.catch((err) =>
				this.setState({
					loading: false,
					questions: [],
				})
			)
	}

	onSubmit = (e) => {
		e.preventDefault()
		const { data } = this.props
		const { questions } = this.state

		let answeredQuestions = {
			section: data.section.name,
			data: [],
		}

		for (const question of questions)
			try {
				const answer = document.querySelector(
					`input[name="answer-${question.id}"]:checked`
				).value

				answeredQuestions.data.push({
					questionId: question.id,
					answer: answer,
				})
			} catch (err) {
				answeredQuestions.data.push({
					questionId: question.id,
					answer: null,
				})
			}

		const config = {
			headers: {
				Accept: 'application/json',
				'Content-Type': 'application/json',
				'Accept-Language': 'en',
			},
		}

		const body = JSON.stringify(answeredQuestions)

		axios
			.post(
				`${process.env.REACT_APP_API_URL}/quizzes/${data.author_slug}/${data.slug}/finish/`,
				body,
				config
			)
			.then((res) => {
				this.setState({ finished_data: res.data })
				clearInterval(this.timer)

				window.scrollTo({ top: 0, behavior: `smooth` })
			})
	}

	onChangePassword = (e) => this.setState({ password: e.target.value })

	matchPasswords = (e) => {
		e.preventDefault()

		const password1 = this.props.data.password
		const password2 = this.state.password

		if (password1 === password2) this.setState({ correctPassword: true })
		else this.setState({ passwordError: 'Incorrect password' })
	}

	componentDidMount = () => {
		if (!this.props.data.password) this.getQuestions()
	}

	componentDidUpdate(prevProps, prevState) {
		if (
			(!this.props.data.password && prevProps.data !== this.props.data) ||
			(prevState.correctPassword !== this.state.correctPassword &&
				this.state.correctPassword)
		)
			this.getQuestions()
	}

	render() {
		const { data } = this.props
		const {
			loading,
			questions,
			timer,
			finished_data,
			sentFeedback,
			password,
			correctPassword,
			passwordError,
		} = this.state

		if (data.question_amount === 0)
			return (
				<div className="message-box info">
					<span className="message-box__text">
						You can't solve this quiz, because it has no questions
					</span>
				</div>
			)

		if (data.password && !correctPassword)
			return (
				<>
					<div className="card">
						<div className="card__body">
							<form
								onSubmit={this.matchPasswords}
								className="auth-form"
							>
								{passwordError ? (
									<div className="message-box error">
										<p className="message-box__text">
											{passwordError}
										</p>
									</div>
								) : null}
								<div className="form-inline">
									<label className="form-inline__label">
										Password:
									</label>
									<input
										type="password"
										value={password}
										onChange={this.onChangePassword}
										className="form-inline__input"
										placeholder="Pass the password..."
										maxLength="20"
										required
									/>
								</div>

								<button
									type="submit"
									className="btn btn__submit btn__contrast"
								>
									Submit
								</button>
							</form>
						</div>
					</div>
					<Ad />
				</>
			)

		return (
			<>
				<Title title={`Start Quiz - ${data.title}`} />

				{timer >= 3 ? (
					<>
						{Object.keys(finished_data).length > 0 ? (
							<div className="card">
								<div className="card__body">
									{data.is_published === false &&
									sentFeedback === false ? (
										<>
											<div className="card__body">
												<FeedbackForm
													ask_name={data.ask_name}
													ask_email={data.ask_email}
													ask_gender={data.ask_gender}
													ask_opinion={
														data.ask_opinion
													}
													score={finished_data.points}
													author_slug={
														data.author_slug
													}
													quiz_slug={data.slug}
													callback={() =>
														this.setState({
															sentFeedback: true,
														})
													}
												/>
											</div>
											<div className="message-box info">
												<span className="message-box__text">
													To see the result you need
													to sent a feedback
												</span>
											</div>
										</>
									) : (
										<>
											<p style={{ fontSize: '1.5rem' }}>
												{data.section.name ===
													'knowledge_quiz' ||
												data.section.name ===
													'universal_quiz' ? (
													<>
														Your score is{' '}
														<span
															style={{
																fontWeight:
																	'600',
															}}
														>
															{
																finished_data.points
															}{' '}
															/ {data.max_score}
														</span>
													</>
												) : null}
												<br />
												<span>
													Your time is{' '}
													<span
														style={{
															fontWeight: '600',
														}}
													>
														{timer - 3}s
													</span>
												</span>
											</p>
											<h3>{finished_data.summery[0]}</h3>
											<p>{finished_data.summery[1]}</p>
										</>
									)}
								</div>
								{data.is_published === true ||
								sentFeedback === true ? (
									<>
										<hr />
										<div className="card__body">
											<OnePageQuiz
												questions={questions}
												section={data.section.name}
												finishedData={finished_data}
											/>
										</div>
									</>
								) : null}
							</div>
						) : (
							<form onSubmit={this.onSubmit}>
								{data.one_page_questions === true ? (
									<OnePageQuiz
										questions={questions}
										section={data.section.name}
										finishedData={finished_data}
									/>
								) : (
									<MultiPageQuiz
										questions={questions}
										section={data.section.name}
										finishedData={finished_data}
									/>
								)}
							</form>
						)}
					</>
				) : loading ? (
					<div className="card card__body auth-form">
						<CircleLoader />
					</div>
				) : (
					<div className="card card__body auth-form">
						<h4>Quiz will start in</h4> <h2>{3 - timer}s</h2>
					</div>
				)}
			</>
		)
	}
}

export default Start
