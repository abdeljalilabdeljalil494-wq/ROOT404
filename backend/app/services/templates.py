"""Platform templates (sujets) — the sample code served to the
workspace per project, plus the hidden judge harnesses.

All samples compile clean under `gcc -Wall -Wextra -Werror`
(verified) and pass their own test suites, so a fresh student
can run the full Moulinette end-to-end right away. Students
are expected to replace/extend this code with their own.
"""

GET_NEXT_LINE_C = r"""
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

#define BUFF_SIZE 32

static char	*rest;

static char	*join_str(const char *a, const char *b)
{
	char	*res;

	res = malloc(strlen(a) + strlen(b) + 1);
	if (!res)
		return (NULL);
	strcpy(res, a);
	strcat(res, b);
	return (res);
}

char	*get_next_line(const int fd)
{
	char	*line;
	char	buf[BUFF_SIZE + 1];
	ssize_t	n;
	char	*nl;

	if (!rest)
		rest = "";
	n = read(fd, buf, BUFF_SIZE);
	if (n < 0)
		return (NULL);
	buf[n] = '\0';
	rest = join_str(rest, buf);
	if (!rest)
		return (NULL);
	nl = strchr(rest, '\n');
	if (nl)
	{
		char	*next;

		line = malloc((size_t)(nl - rest) + 1);
		if (!line)
			return (NULL);
		memcpy(line, rest, (size_t)(nl - rest));
		line[nl - rest] = '\0';
		next = malloc(strlen(nl + 1) + 1);
		if (!next)
		{
			free(line);
			return (NULL);
		}
		strcpy(next, nl + 1);
		free(rest);
		rest = next;
		return (line);
	}
	if (n == 0)
	{
		line = rest;
		rest = NULL;
		if (!*line)
		{
			free(line);
			return (NULL);
		}
		return (line);
	}
	line = rest;
	rest = NULL;
	return (line);
}
"""

GNL_HARNESS_C = r"""
#include <fcntl.h>
#include <stdio.h>
#include <string.h>
#include <unistd.h>

#include "get_next_line.c"

int	main(void)
{
	char	*line;
	int		fd;
	int		ok1;
	int		ok2;
	int		f;

	f = open("/tmp/root404_gnl_input", O_WRONLY | O_CREAT | O_TRUNC, 0644);
	if (f < 0)
		return (1);
	if (write(f, "abc\ndef\nghi", 11) != 11)
		return (1);
	close(f);
	fd = open("/tmp/root404_gnl_input", O_RDONLY);
	if (fd < 0)
		return (1);

	ok1 = 1;
	line = get_next_line(fd);
	ok1 = ok1 && line && strcmp(line, "abc") == 0;
	free(line);
	line = get_next_line(fd);
	ok1 = ok1 && line && strcmp(line, "def") == 0;
	free(line);
	line = get_next_line(fd);
	ok1 = ok1 && line && strcmp(line, "ghi") == 0;
	free(line);
	printf(ok1 ? "T1 OK\n" : "T1 KO\n");

	ok2 = 1;
	line = get_next_line(fd);
	ok2 = (line == NULL);
	free(line);
	line = get_next_line(fd);
	ok2 = ok2 && (line == NULL);
	printf(ok2 ? "T2 OK\n" : "T2 KO\n");
	close(fd);
	unlink("/tmp/root404_gnl_input");
	return (ok1 && ok2 ? 0 : 1);
}
"""

FT_PRINTF_C = r"""
#include <stdarg.h>
#include <stdio.h>
#include <string.h>
#include <unistd.h>

static void	put_str(const char *s)
{
	size_t	i;

	if (!s)
		return;
	i = 0;
	while (s[i])
	{
		write(1, &s[i], 1);
		i++;
	}
}

static void	put_num(long n)
{
	char	buf[24];
	int		i;

	if (n == 0)
	{
		put_str("0");
		return;
	}
	if (n < 0)
	{
		put_str("-");
		n = -n;
	}
	i = 0;
	while (n > 0)
	{
		buf[i++] = (char)('0' + (n % 10));
		n /= 10;
	}
	while (i > 0)
		write(1, &buf[--i], 1);
}

void	ft_printf(const char *str, ...)
{
	va_list	ap;

	if (!str)
		return;
	va_start(ap, str);
	while (*str)
	{
		if (*str == '%' && str[1])
		{
			char	c;

			str++;
			if (*str == 's')
				put_str(va_arg(ap, char *));
			else if (*str == 'd')
				put_num(va_arg(ap, int));
			else if (*str == 'c')
			{
				c = (char)va_arg(ap, int);
				write(1, &c, 1);
			}
			else
				put_str("%");
			str++;
		}
		else
		{
			write(1, str, 1);
			str++;
		}
	}
	va_end(ap);
}
"""

FT_PRINTF_HARNESS_C = r"""
#include "ft_printf.c"

int	main(void)
{
	ft_printf("T1: %d %s %c\n", 42, "root404", 'X');
	ft_printf("T2: %d%% %s\n", -17, "ok");
	return (0);
}
"""

PHILOSOPHERS_C = r"""
#include <pthread.h>
#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include <unistd.h>

static int			g_n;
static long			g_start;
static pthread_mutex_t	*forks;
static pthread_mutex_t	g_print;

static long	now_raw_ms(void)
{
	struct timespec	ts;

	clock_gettime(CLOCK_REALTIME, &ts);
	return (ts.tv_sec * 1000 + ts.tv_nsec / 1000000);
}

static long	now_ms(void)
{
	return (now_raw_ms() - g_start);
}

typedef struct ph
{
	int	id;
	int	meals;
} t_ph;

static void	*philosoph(void	*arg)
{
	t_ph	*p;

	p = (t_ph *)arg;
	while (p->meals > 0)
	{
		pthread_mutex_lock(&g_print);
		printf("%ld P%d is thinking\n", now_ms(), p->id);
		pthread_mutex_unlock(&g_print);
		usleep(5);
		pthread_mutex_lock(&forks[p->id]);
		pthread_mutex_lock(&forks[(p->id + 1) % g_n]);
		pthread_mutex_lock(&g_print);
		printf("%ld P%d is eating\n", now_ms(), p->id);
		pthread_mutex_unlock(&g_print);
		usleep(5);
		pthread_mutex_unlock(&forks[(p->id + 1) % g_n]);
		pthread_mutex_unlock(&forks[p->id]);
		p->meals--;
		pthread_mutex_lock(&g_print);
		printf("%ld P%d is sleeping\n", now_ms(), p->id);
		pthread_mutex_unlock(&g_print);
		usleep(5);
	}
	return (NULL);
}

int	main(int argc, char **argv)
{
	pthread_t	*threads;
	t_ph		*phs;
	int			i;

	if (argc != 3)
	{
		printf("usage: philosophers <n> <meals>\n");
		return (1);
	}
	g_n = atoi(argv[1]);
	phs = (t_ph *)malloc(sizeof(t_ph) * (size_t)g_n);
	threads = (pthread_t *)malloc(sizeof(pthread_t) * (size_t)g_n);
	forks = (pthread_mutex_t *)malloc(sizeof(pthread_mutex_t) * (size_t)g_n);
	if (!phs || !threads || !forks)
		return (1);
	g_start = now_raw_ms();
	pthread_mutex_init(&g_print, NULL);
	for (i = 0; i < g_n; i++)
	{
		pthread_mutex_init(&forks[i], NULL);
		phs[i].id = i;
		phs[i].meals = atoi(argv[2]);
		if (pthread_create(&threads[i], NULL, philosoph, &phs[i]) != 0)
			return (1);
	}
	for (i = 0; i < g_n; i++)
		pthread_join(threads[i], NULL);
	return (0);
}
"""

MINISHELL_C = r"""
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/wait.h>
#include <unistd.h>

static int	builtin_echo(int argc, char **argv)
{
	int	i;

	i = 1;
	while (i < argc)
	{
		if (i > 1)
			fputc(' ', stdout);
		fputs(argv[i], stdout);
		i++;
	}
	fputc('\n', stdout);
	return (0);
}

int	main(void)
{
	char	buf[512];
	char	*argv[64];
	char	*save;
	pid_t	pid;
	int		argc;
	int		st;

	while (1)
	{
		fputs("minishell$ ", stdout);
		fflush(stdout);
		if (!fgets(buf, sizeof(buf), stdin))
			break;
		buf[strcspn(buf, "\n")] = '\0';
		if (!*buf)
			continue;
		argc = 0;
		save = NULL;
		{
			char	*tok;

			tok = strtok_r(buf, " \t", &save);
			while (tok && argc < 63)
			{
				argv[argc++] = tok;
				tok = strtok_r(NULL, " \t", &save);
			}
		}
		argv[argc] = NULL;
		if (!argc)
			continue;
		if (strcmp(argv[0], "echo") == 0)
		{
			builtin_echo(argc, argv);
			continue;
		}
		pid = fork();
		if (pid == 0)
		{
			execvp(argv[0], argv);
			fprintf(stderr, "minishell: %s: command not found\n", argv[0]);
			return (127);
		}
		if (pid > 0)
		{
			waitpid(pid, &st, 0);
		}
	}
	return (0);
}
"""

MAIN_GENERIC_C = r"""
#include <stdio.h>

int	main(void)
{
	printf("ROOT 404 — sujet prêt : ton code remplacera ce squelette.\n");
	return (0);
}
"""
