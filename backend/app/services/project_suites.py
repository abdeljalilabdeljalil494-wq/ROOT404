"""Versioned executable foundations curriculum, not replacement for 42 projects.

Every supported runner language has an actual stdin/stdout suite. Existing advanced
projects retain their scope and stay unavailable until project-specific harnesses
are authored; passing a sum exercise must never validate minishell/libft/etc.
"""
import random
from app.models.project import Project

LANGUAGES = {'c': 'C', 'cpp': 'C++', 'python': 'Python', 'javascript': 'JavaScript'}
SPEC = ('Read zero to 1000 whitespace-separated signed decimal integers from stdin '
        'until EOF. Each is between -1000000000 and 1000000000. Output their sum '
        'as a base-10 integer and a newline. An empty input sums to zero. '
        'Use a 64-bit integer or exact equivalent. No prompts or extra output.')


def sum_suite():
    rng = random.Random(40401)
    values = [[], [0], [42], [-1, 1], [1000000000]*500, [-1000000000]*500, [0]*1000,
              [rng.randint(-1000000000, 1000000000) for _ in range(97)], [3, -2, 9, -15, 5]]
    cases = [{'stdin': ' '.join(map(str, items)) + ('\n' if items else ''),
              'expected_stdout': str(sum(items)) + '\n'} for items in values]
    cases.append({'stdin': '\t 1\n\n-2\t 3   \n', 'expected_stdout': '2\n'})
    return cases


def seed_execution_projects(db):
    added = []
    for language, label in LANGUAGES.items():
        slug = f'foundations-sum-{language}'
        if db.query(Project).filter_by(slug=slug).first():
            continue  # Never overwrite catalog data or instructor edits silently.
        db.add(Project(slug=slug, name=f'Stream Sum — {label}', description=SPEC,
                       long_description=SPEC, lang=label, level_value=0, level='Foundations',
                       xp=100, difficulty=1, status_default='available', duration='1 h',
                       objectives=['Parse stdin', 'Handle EOF and signed 64-bit sums'],
                       test_cases=sum_suite(), norm_rules={'suite_version': 'stream-sum-v1',
                                                         'allowed_languages': [language]}))
        added.append(slug)
    db.commit()
    return {'created': added, 'note': 'Only these foundation projects have supplied suites; advanced projects unchanged'}
