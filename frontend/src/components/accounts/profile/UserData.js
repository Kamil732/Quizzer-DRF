import React, { Component } from 'react'
import PropTypes from 'prop-types'
import { FaEdit } from 'react-icons/fa'
import Textarea from '../../../common/Textarea'

class UserData extends Component {
    static propTypes = {
        isOwner: PropTypes.bool,
        picture_url: PropTypes.string,
        username: PropTypes.string.isRequired,
        bio: PropTypes.string.isRequired,
        quizzes_count: PropTypes.number.isRequired,
        quizzes_solves: PropTypes.number.isRequired,
        errors: PropTypes.object,
        removeError: PropTypes.func.isRequired,
        updateUserData: PropTypes.func.isRequired,
    }

    constructor(props) {
        super(props)

        this.state = {
            picture: null,
            picturePreview: this.props.picture_url,
            username: this.props.username,
            bio: this.props.bio,
            picture_edit_mode: false,
            username_edit_mode: false,
            bio_edit_mode: false,
        }

        this.onChange = this.onChange.bind(this)
        this.onSubmit = this.onSubmit.bind(this)
    }

    onChange = e => this.setState({ [e.target.name]: e.target.value })

    handleImageChange = e => {
        this.setState({
            picture: e.target.files[0],
            picturePreview: URL.createObjectURL(e.target.files[0]),
        })
    }

    componentDidUpdate(prevProps, _) {
        if (prevProps.username !== this.props.username || prevProps.bio !== this.props.bio)
            this.setState({
                username: this.props.username,
                bio: this.props.bio,
            })
    }

    onSubmit = async (e, field) => {
        e.preventDefault()

        console.log(this.state[field])

        this.props.removeError(field)
        await this.props.updateUserData({ [field]: this.state[field] }, false)

        if (this.props.errors[field] === undefined)
            this.setState({ [`${field}_edit_mode`]: false })
    }

    render() {
        const { isOwner, quizzes_count, quizzes_solves, errors } = this.props
        const { picturePreview, username, bio, username_edit_mode, bio_edit_mode } = this.state

        return (
            <>
                <div className="card">
                    <div className="card__header">{ isOwner ? 'My Profile' : `${username}'s Profile` }</div>
                    <div className="card__body">
                        <div className="profile">
                            <div className={`profile__img ${isOwner ? 'owner' : ''}`}>
                                <img src={picturePreview} alt={username} draggable="false" className="img-rounded" />
                                {
                                    isOwner ? (
                                        <form onSubmit={e => this.onSubmit(e, 'picture')}>
                                            {
                                                errors.picture ? (
                                                    <div className="error-box">
                                                        {
                                                            errors.picture.map((error, index) => (
                                                                <p className="error-text" key={index}>{error}</p>
                                                            ))
                                                        }
                                                    </div>
                                                ) : null
                                            }

                                            <input
                                                type="file"
                                                accept="image/png, image/jpeg"
                                                className="btn btn__edit"
                                                onChange={this.handleImageChange}
                                            />
                                            <button className="btn">
                                                Save
                                            </button>
                                        </form>
                                    ) : null
                                }
                            </div>

                            <div className="profile__content">
                                <div className="profile__username">
                                    {
                                        username_edit_mode ? (
                                            <form onSubmit={e => this.onSubmit(e, 'username')}>
                                                {
                                                    errors.username ? (
                                                        <div className="error-box">
                                                            {
                                                                errors.username.map((error, index) => (
                                                                    <p className="error-text" key={index}>{error}</p>
                                                                ))
                                                            }
                                                        </div>
                                                    ) : null
                                                }
                                                <div className="form-control">
                                                    <input
                                                        type="text"
                                                        name="username"
                                                        className="form-control__input"
                                                        value={username}
                                                        onChange={this.onChange}
                                                    />
                                                </div>
                                                <button className="btn">
                                                    Save
                                                </button>
                                            </form>
                                        ) : (
                                            <>
                                                {username}
                                                {
                                                    isOwner ? (
                                                        <button className="btn__edit" onClick={() => this.setState({ username_edit_mode: true })}>
                                                            Edit <FaEdit />
                                                        </button>
                                                    ) : null
                                                }
                                            </>
                                        )
                                    }
                                </div>
                                <div className="profile__bio">
                                    {
                                        bio_edit_mode ? (
                                            <form onSubmit={e => this.onSubmit(e, 'bio')}>
                                                {
                                                    errors.bio ? (
                                                        <div className="error-box">
                                                            {
                                                                errors.bio.map((error, index) => (
                                                                    <p className="error-text" key={index}>{error}</p>
                                                                ))
                                                            }
                                                        </div>
                                                    ) : null
                                                }
                                                <div className="form-control">
                                                    <Textarea
                                                        name="bio"
                                                        value={bio}
                                                        onChange={this.onChange}
                                                        className="form-control__input form-control__textarea"
                                                        rows="10"
                                                    />
                                                </div>
                                                <button className="btn">
                                                    Save
                                                </button>
                                            </form>
                                        ) : (
                                            <>
                                                { bio ? bio : 'Welcome to my profile!' }
                                                {
                                                    isOwner ? (
                                                        <button className="btn__edit" onClick={() => this.setState({ bio_edit_mode: true })}>
                                                            Edit <FaEdit />
                                                        </button>
                                                    ) : null
                                                }
                                            </>
                                        )
                                    }
                                </div>
                                <p style={{ fontSize: '1.1rem' }}>
                                    QUIZZES: {quizzes_count}
                                    &nbsp;&nbsp;
                                    &bull;
                                    &nbsp;&nbsp;
                                    SOLVES: {quizzes_solves}
                                </p>
                            </div>
                        </div>
                    </div>
                </div>
            </>
        )
    }
}

export default UserData
