import React, { Component } from 'react'
import axios from 'axios'
import CircleLoader from '../../components/loaders/CircleLoader'
import Title from '../../common/Title'

import AboutUser from '../../components/accounts/profile/AboutUser'
import FacebookShare from '../../components/social_media/FacebookShare'
import TwitterShare from '../../components/social_media/TwitterShare'
import { Redirect } from 'react-router-dom'

export class Detail extends Component {
    constructor(props) {
        super(props)

        this.state = {
            loading: true,
            data: {},
        }

        this.getQuizData = this.getQuizData.bind(this)
    }

    async getQuizData() {
        const { author_slug, quiz_slug } = this.props.match.params

        try {
            const res = await axios.get(`${process.env.REACT_APP_API_URL}/quizzes/${author_slug}/${quiz_slug}/`)

            this.setState({
                loading: false,
                data: res.data,
            })
        } catch (err) {
            this.setState({
                loading: false,
                data: [],
            })
        }
    }

    componentDidMount = () => this.getQuizData()

    componentDidUpdate(prevProps, _) {
        if (prevProps.match.params.author_slug !== this.props.match.params.author_slug ||
            prevProps.match.params.quiz_slug !== this.props.match.params.quiz_slug)
            this.getQuizData()
    }

    render() {
        const { loading, data } = this.state

        if (loading)
            return <CircleLoader />
        else if (Object.keys(data).length === 0)
            return <Redirect to="/not-found" />

        return (
            <>
                <Title title={`Quiz Detail ${data.title}`} />

                <div className="row">
                    <div className="col col-sm-9">
                        <div className="card__header">
                            {data.title}
                        </div>
                        <div className="card">
                            <div className="card__body">
                                <div className="quiz-detail">
                                    <img className="quiz-detail__img" src={data.image_url} alt={data.title} />
                                    {data.description}
                                </div>
                            </div>

                            <hr />

                        <div className="card__body share-items">
                            <FacebookShare url={window.location.href} quote={data.title} image_url={data.image_url} />
                            <TwitterShare url={window.location.href} title={data.title} />
                        </div>
                        </div>
                        <div className="card__footer">
                            <button className="btn btn__submit btn__contrast">START</button>
                        </div>
                    </div>
                    <div className="col col-sm-3">
                        <AboutUser
                            accountUrl={data.author}
                        />
                    </div>
                </div>
            </>
        )
    }
}

export default Detail
