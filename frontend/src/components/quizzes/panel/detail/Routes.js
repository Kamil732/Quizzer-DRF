import React from 'react'
import { Redirect, Switch } from 'react-router-dom'
import PrivateRoute from '../../../../common/PrivateRoute'
import Privacy from '../../../../containers/quizzes/panel/detail/Privacy'
import Settings from '../../../../containers/quizzes/panel/detail/Settings'
import Summery from '../../../../containers/quizzes/panel/detail/Summery'

function Routes(props) {
    return (
        <Switch>
            <PrivateRoute exact path="/panel/dashboard/:quiz_slug/summery" component={() => <Summery {...props} />} />
            <PrivateRoute exact path="/panel/dashboard/:quiz_slug/settings" component={() => <Settings {...props} />} />
            <PrivateRoute exact path="/panel/dashboard/:quiz_slug/privacy" component={() => <Privacy {...props} />} />

            <Redirect to="/not-found" />
        </Switch>
    )
}

export default Routes