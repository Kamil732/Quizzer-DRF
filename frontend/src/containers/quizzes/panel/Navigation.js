import React from 'react'

import ActiveTag from '../../../components/navigation/ActiveTag'
import Ad from '../../../components/Ad'
import PrivateRoute from '../../../common/PrivateRoute'
import Create from '../Create'
import Dashboard from './Dashboard'
import { Redirect, Switch } from 'react-router-dom'

function Navigation() {
    return (
        <div className="row">
            <div className="col col-sm-3">
                <nav className="vertical-menu card">
                    <ActiveTag to={['/panel/dashboard']} className="vertical-menu__item">Dashboard</ActiveTag>
                    <ActiveTag to={['/panel/settings']} className="vertical-menu__item">Account Settings</ActiveTag>
                    <ActiveTag to={['/panel/create-quiz']} className="vertical-menu__item">Create Quiz</ActiveTag>
                </nav>
                <Ad />
            </div>
            <div className="col col-sm-9">
                <Switch>
                    <PrivateRoute exact path="/panel/create-quiz" component={Create} />
                    <PrivateRoute exact path="/panel/dashboard" component={Dashboard} />

                    <Redirect to="/not-found" />
                </Switch>
            </div>
        </div>
    )
}

export default Navigation