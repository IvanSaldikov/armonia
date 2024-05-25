from typing import TypedDict

from django.utils.text import slugify

from common.utils.helpers import HelperUtils
from config.logger import get_module_logger
from countries.consts.nationalities import NATIONALITIES
from problems.models import Problem
from users.models import User

logger = get_module_logger("Problem Utils")


class ProblemTypeMinimum(TypedDict):
    author: User
    problem_type: str
    problem_description: str
    user_age: int
    therapist_name: str
    therapist_gender: str
    therapist_country: str


class ProblemManager:

    @classmethod
    def create_problem(cls, params: ProblemTypeMinimum) -> Problem:
        problem: Problem = Problem(**params)
        problem.slug = f"{str(problem.author.uuid)}_{slugify(problem.problem_type)}_{HelperUtils.generate_snowflake_id()}"
        problem.save()
        return problem

    @classmethod
    def get_problem_by_slug(cls, slug: str, user: User) -> Problem | None:
        problem = Problem.objects.filter(slug=slug, is_active=True, is_public=True).first()
        if not problem:
            problem = Problem.objects.filter(slug=slug, is_active=True, author=user).first()
        return problem

    @classmethod
    def get_default_problem(cls):
        return Problem.objects.first()

    @classmethod
    def get_nationality_for_ai_therapist(cls, problem: Problem) -> str:
        return NATIONALITIES.get(problem.therapist_country.code, {}).get("nationality", "")

    @classmethod
    def get_extra_data_for_problem(cls, problem: Problem) -> str:
        extra_data = ""
        if problem.therapist_country:
            extra_data += f"You are from {problem.therapist_country.name}. "
        if problem.therapist_name:
            extra_data += f"Your name is {problem.therapist_name}. "
        if problem.therapist_gender:
            extra_data += f"You are {problem.therapist_gender}. "
        if problem.problem_type:
            extra_data += f"User set the problem type as {problem.problem_type}. "
        if problem.problem_description:
            extra_data += f'User provided this initial description of the problem to solve: "{problem.problem_type}". '
        if problem.user_age:
            extra_data += f'User age is {problem.user_age}. Please try to consider this when appropriate. '
        return extra_data
