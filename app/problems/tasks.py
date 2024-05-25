from celery import shared_task


@shared_task
def generate_avatar_for_problem(problem_id: int) -> str:
    from problems.utils import ProblemManager
    from problems.models import Problem
    problem = Problem.objects.get(id=problem_id)
    # For future if we want to generate avatars or something
    return ProblemManager.generate_avatar_for_problem(problem=problem)
