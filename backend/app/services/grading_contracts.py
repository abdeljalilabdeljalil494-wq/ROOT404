"""Original catalog eligibility. Descriptions are NOT authoritative subjects.

Do not register a project by assigning generic stdin/stdout rows in the database.
A future approved harness must be a separately reviewed trusted implementation.
No original project is registered yet; do not invent an ABI/rubric to fill a gap.
"""
ORIGINAL_PROJECTS = {
    'get_next_line': ('C','Multiple FD support and variable BUFFER_SIZE are stated in the seed objectives.'),
    'ft_printf': ('C','Variadic libc-style formatting is described; exact conversions/bonus ABI absent.'),
    'minishell': ('C','Parsing, pipes, redirections, builtins and signals are described; exact subject absent.'),
    'philosophers': ('C','Threads, mutexes and absence of data races are described; timing/CLI rubric absent.'),
    'netpractice': ('Network','TCP/IP configuration and subnet masks are described; topology/artifact schema absent.'),
    'cub3d': ('C','Raycasting graphics is described; map/assets/graphics-library contract absent.'),
    'webserv': ('C++','Nonblocking HTTP/1.1 is described; protocol/config/CGI acceptance details absent.'),
    'inception': ('Docker','Docker Compose infrastructure is described; required services/security rubric absent.'),
    'ft_transcendence': ('Web','Realtime SPA and multiplayer Pong are described; selected modules/contracts absent.'),
}


def original_eligibility(slug):
    if slug not in ORIGINAL_PROJECTS: return None
    language,facts=ORIGINAL_PROJECTS[slug]
    return {'project':slug,'language':language,'known_source_facts':facts,
            'specification':'BLOCKED','harness':'INCOMPLETE','execution_evidence':'BLOCKED',
            'grading_enabled':False}
