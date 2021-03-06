# -*- coding: utf-8 -*-

import pytz
import datetime
import pkg_resources

from django.template import Context, Template
from django.utils.encoding import smart_text

from xblock.core import XBlock
from xblock.fields import Scope, Integer, String, Boolean
from xblock.fragment import Fragment

from xmodule.util.duedate import get_extended_due_date


class TxtXBlock(XBlock):
    display_name = String(
        display_name=u"Название",
        help=u"Название задания, которое увидят студенты.",
        default=u'txt',
        scope=Scope.settings
    )

    question = String(
        display_name=u"Вопрос",
        help=u"Текст задания.",
        default=u"Вы готовы?",
        scope=Scope.settings
    )

    correct_answer = String(
        display_name=u"Правильный ответ",
        help=u"Правильный ответ",
        default="",
        scope=Scope.settings
    )

    weight = Integer(
        display_name=u"Максимальное количество баллов",
        help=(u"Максимальное количество баллов",
              u"которое может получить студент."),
        default=100,
        scope=Scope.settings
    )

    max_attempts = Integer(
        display_name=u"Максимальное количество попыток",
        help=u"",
        default=0,
        scope=Scope.settings
    )

    attempts = Integer(
        display_name=u"Количество сделанных попыток",
        default=0,
        scope=Scope.user_state
    )

    points = Integer(
        display_name=u"Количество баллов студента",
        default=None,
        scope=Scope.user_state
    )

    answer = String(
        display_name=u"Ответ пользователя",
        default="",
        scope=Scope.user_state
    )

    keywords = String(
        display_name=u"Слова, вхождение которых обязательно.",
        help=u"Обязательные слова",
        default="",
        scope=Scope.settings
    )

    grading_threshold = Integer(
        display_name=u"Количество баллов студента",
        default=None,
        scope=Scope.settings
    )

    has_score = True

    @staticmethod
    def resource_string(path):
        """
        Handy helper for getting resources from our kit.
        """
        data = pkg_resources.resource_string(__name__, path)
        return data.decode("utf8")

    @staticmethod
    def load_resources(js_urls, css_urls, fragment):
        """
        Загрузка локальных статических ресурсов.
        """
        for js_url in js_urls:

            if js_url.startswith('public/'):
                fragment.add_javascript_url(self.runtime.local_resource_url(self, js_url))
            elif js_url.startswith('static/'):
                fragment.add_javascript(_resource(js_url))
            else:
                pass

        for css_url in css_urls:

            if css_url.startswith('public/'):
                fragment.add_css_url(self.runtime.local_resource_url(self, css_url))
            elif css_url.startswith('static/'):
                fragment.add_css(_resource(css_url))
            else:
                pass

    def past_due(self):
            """
            Проверка, истекла ли дата для выполнения задания.
            """
            due = get_extended_due_date(self)
            if due is not None:
                if _now() > due:
                    return False
            return True

    def is_course_staff(self):
        """
        Проверка, является ли пользователь автором курса.
        """
        return getattr(self.xmodule_runtime, 'user_is_staff', False)

    def is_instructor(self):
        """
        Проверка, является ли пользователь инструктором.
        """
        return self.xmodule_runtime.get_user_role() == 'instructor'

    # views

    def studio_view(self, *args, **kwargs):
        """
        Отображение txtXBlock разработчику (CMS).
        """
        context = {
            "display_name": self.display_name,
            "weight": self.weight,
            "question": self.question,
            "correct_answer": self.correct_answer,
            "answer": self.answer,
            "max_attempts": self.max_attempts,
        }

        fragment = Fragment()
        fragment.add_content(
            render_template(
                'static/html/txt_edit.html',
                context
            )
        )

        js_urls = (
            "static/js/txt_edit.js",
        )

        css_urls = (
            'static/css/txt.css',
        )

        self.load_resources(js_urls, css_urls, fragment)
        fragment.initialize_js('TxtXBlockEdit')

        return fragment

    def student_view(self, *args, **kwargs):
        """
        Отображение txtXBlock студенту (LMS).
        """

        context = {
            "display_name": self.display_name,
            "weight": self.weight,
            "question": self.question,
            "correct_answer": self.correct_answer,
            "answer": self.answer,
            "attempts": self.attempts,
        }

        if self.max_attempts != 0:
            context["max_attempts"] = self.max_attempts

        if self.past_due():
            context["past_due"] = True

        if self.answer != '{}':
            context["points"] = self.points

        if answer_opportunity(self):
            context["answer_opportunity"] = True

        if self.is_course_staff() is True or self.is_instructor() is True:
            context['is_course_staff'] = True

        fragment = Fragment()
        fragment.add_content(
            render_template(
                'static/html/txt.html',
                context
            )
        )

        js_urls = (
            'static/js/txt.js',
        )

        css_urls = (
            'static/css/txt.css',
        )

        self.load_resources(js_urls, css_urls, fragment)

        fragment.initialize_js('TxtXBlock')
        return fragment

    # handlers

    @XBlock.json_handler
    def studio_submit(self, data, suffix=''):
        self.display_name = data.get('display_name')
        self.question = data.get('question')
        self.weight = data.get('weight')
        self.correct_answer = data.get('correct_answer')
        self.max_attempts = data.get('max_attempts')
        self.keywords = data.get('keywords')
        self.grading_threshold = data.get('grading_threshold')

        return {'result': 'success'}

    @XBlock.json_handler
    def student_submit(self, data, suffix=''):
        pass


def answer_opportunity(self):
    """
    Возможность ответа (если количество сделанное попыток меньше заданного).
    """
    if self.max_attempts <= self.attempts and self.max_attempts != 0:
        return False
    else:
        return True


def _now():
    """
    Получение текущих даты и времени.
    """
    return datetime.datetime.utcnow().replace(tzinfo=pytz.utc)


def _resource(path):  # pragma: NO COVER
    """
    Handy helper for getting resources from our kit.
    """
    data = pkg_resources.resource_string(__name__, path)
    return data.decode("utf8")


def render_template(template_path, context=None):
    """
    Evaluate a template by resource path, applying the provided context.
    """
    if context is None:
        context = {}

    template_str = load_resource(template_path)
    template = Template(template_str)
    return template.render(Context(context))


def load_resource(resource_path):
    """
    Gets the content of a resource
    """
    try:
        resource_content = pkg_resources.resource_string(__name__, resource_path)
        return smart_text(resource_content)
    except EnvironmentError:
        pass
