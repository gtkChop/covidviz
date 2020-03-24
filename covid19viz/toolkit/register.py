import dash
from covid19viz.plugin import CovIdDashBoardAPIPlugin
from covid19viz.utils import helper as h
from covid19viz.toolkit import APIGetActions, APIPostActions
from covid19viz.utils import errors
from covid19viz.controller.controller import APIResponseObject
import logging

log = logging.getLogger(__name__)


class RegisterDashApplication(CovIdDashBoardAPIPlugin):

    def __init__(self):
        CovIdDashBoardAPIPlugin.__init__(self)
        self._app = dash.Dash(
            __name__,
            assets_folder=h.get_static_dir_path()
        )

    @property
    def app(self):
        self.prepare_app()
        return self._app

    def register_actions(self):
        """
        Register all the routes to the dash board. Only css route is added
        :return: None
        """
        for action in self.api_action():
            if action['type'] == "GET":
                log.info("Setting GET action: {}".format(action.get('action')))
                setattr(APIGetActions, action.get('action'), staticmethod(action.get('module')))
            elif action['type'] == "POST":
                log.info("Setting POST action: {}".format(action.get('action')))
                setattr(APIPostActions, action.get('action'), staticmethod(action.get('module')))
            else:
                raise errors.PluginError("Not Implemented - supports GET or POST actions")

        log.info("Adding API route..")
        self._app._add_url("{}/<action_name>".format(self.api_url), view_func=APIResponseObject.actions)

    def prepare_app(self):
        """
        Add all layout and components to the dash application
        :return: None
        """

        import os
        import logging.config
        logging_cnf = os.getcwd() + '/logger.ini'
        logging.config.fileConfig(logging_cnf)
        log.info("Starting Application...............")
        # Register routes. This is used to call css
        self.register_actions()

        # Header
        log.info("Gathering dash header component")
        header = self.dash_header()

        # Footer
        log.info("Gathering dash footer")
        footer = self.dash_footer()

        # Load components
        log.info("Loading dash components")
        children = []
        _components = self.dash_components()

        for _c in _components:
            children.append(_components.get(_c))

        # Gets dash layout
        self._app.layout = self.dash_layout()(header, children, footer)

        callbacks = self.dash_callbacks()

        # TODO: Validate the callback
        log.info("Adding dash callbacks")
        for callback in callbacks:
            self._app.callback(
                callback.get('output'),
                callback.get('input'),
                callback.get('state')
            )(callback.get('module'))
