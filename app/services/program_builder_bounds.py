"""Count source rows and source text in SQLite before ORM relationship loads."""

from sqlalchemy import LargeBinary, cast, func, select

from app.models.user_program import (
    UserProgram,
    UserProgramExercise,
    UserProgramQualityReview,
    UserProgramRepTarget,
    UserProgramSession,
)

MAX_SOURCE_ROWS = 1000
MAX_SOURCE_TEXT_BYTES = 131072


def bounded_program_ids(db, owner, program_ids=None):
    """Bound the root scan independently of each root's descendant budget."""
    from app.services.program_builder_commands import ProgramBuilderError

    query = select(UserProgram.id).where(UserProgram.user_id == owner)
    if program_ids is not None:
        query = query.where(UserProgram.id.in_(program_ids))
    result = list(db.scalars(query.order_by(UserProgram.id).limit(MAX_SOURCE_ROWS + 1)))
    if len(result) > MAX_SOURCE_ROWS:
        raise ProgramBuilderError("source_too_large", 413)
    return result


def check_source_budget(db, owner, program_ids=None):
    for program_id in bounded_program_ids(db, owner, program_ids):
        _check_program_budget(db, owner, program_id)


def _check_program_budget(db, owner, program_id):
    from app.services.program_builder_commands import ProgramBuilderError

    roots = select(UserProgram.id).where(UserProgram.user_id == owner, UserProgram.id == program_id)
    sessions = select(UserProgramSession.id).where(UserProgramSession.user_program_id.in_(roots))
    slots = select(UserProgramExercise.id).where(
        UserProgramExercise.user_program_session_id.in_(sessions)
    )
    queries = [
        (UserProgram, UserProgram.id.in_(roots)),
        (UserProgramSession, UserProgramSession.id.in_(sessions)),
        (UserProgramExercise, UserProgramExercise.id.in_(slots)),
        (UserProgramRepTarget, UserProgramRepTarget.user_program_exercise_id.in_(slots)),
        (UserProgramQualityReview, UserProgramQualityReview.user_program_id.in_(roots)),
    ]
    total = 0
    for model, condition in queries:
        total += db.scalar(select(func.count()).select_from(model).where(condition))
        if total > MAX_SOURCE_ROWS:
            raise ProgramBuilderError("source_too_large", 413)
        text_columns = [c for c in model.__table__.columns if c.type.python_type is str]
        if text_columns:
            size = (
                db.scalar(
                    select(
                        func.sum(
                            sum(
                                func.coalesce(func.length(cast(c, LargeBinary)), 0)
                                for c in text_columns
                            )
                        )
                    )
                    .select_from(model)
                    .where(condition)
                )
                or 0
            )
            if size > MAX_SOURCE_TEXT_BYTES:
                raise ProgramBuilderError("source_too_large", 413)
