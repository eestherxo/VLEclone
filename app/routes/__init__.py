from .auth import auth_bp
from .courses import course_bp
from .events import event_bp
from .forum import forum_bp
from .threads import thread_bp
from .content import content_bp
from .assignments import assignment_bp
from .reports import report_bp

__all__ = ['auth_bp', 'course_bp', 'event_bp', 'forum_bp', 'thread_bp', 'content_bp', 'assignment_bp', 'report_bp']