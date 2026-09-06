/**
 * Mock domain data for ROOT 404.
 * Mirrors the shapes the FastAPI backend is expected to return, so swapping
 * `services/api.js` from mock → real HTTP requires no component changes.
 */

export const currentUser = {
  id: 'u_001',
  username: 'abdeljalil',
  displayName: 'Abdeljalil',
  fullName: 'Abdeljalil Ben Youssef',
  title: 'Coder — Cursus Systèmes',
  campus: 'Tunis',
  coalition: { name: 'The Phoenix', color: '#F8851F', rank: 2, points: 7286 },
  avatar: 'https://i.pravatar.cc/160?img=13',
  level: 6.42,
  levelProgress: 42,
  xp: 24780,
  xpToNext: 2240,
  projectsDone: 38,
  correctionPoints: 1250,
  accountValue: 2450,
  jetons: 4,
  streak: 24,
  accuracy: 81,
  reputation: 88,
  integrity: 96,
  blackHole: { daysLeft: 87, total: 120 },
  joined: 'Sept. 2025',
  bio: "Étudiant en systèmes & réseaux. J'aime le C, les pointeurs et les segfaults à 3h du matin.",
  socials: { github: 'abdeljalil', discord: 'abdeljalil#404', site: 'root404.tn/u/abdeljalil' },
}

export const navLinks = [
  { label: 'Accueil', to: '/' },
  { label: 'À propos', to: '/about' },
  { label: 'Parcours', to: '/parcours' },
  { label: 'Piscine', to: '/piscine' },
  { label: 'Classement', to: '/classement' },
  { label: 'Communauté', to: '/communaute' },
  { label: 'Blog', to: '/blog' },
]

export const heroFeatures = [
  {
    icon: 'Terminal',
    title: 'Environnement Isolé',
    text: 'Exécute ton code dans des conteneurs Docker sécurisés et identiques pour tous.',
  },
  {
    icon: 'Users',
    title: 'Évaluation Pair à Pair',
    text: "Apprends en corrigeant et en étant corrigé par d'autres étudiants.",
  },
  {
    icon: 'Trophy',
    title: 'Gamification',
    text: 'Gagne des XP, monte de niveau et débloque des récompenses.',
  },
  {
    icon: 'Brain',
    title: 'Assistant IA',
    text: "Un assistant intelligent qui t'aide à comprendre, pas à copier.",
  },
  {
    icon: 'ShieldCheck',
    title: 'Anti-Cheating',
    text: 'Système de détection de fraude avancé pour un jeu équitable.',
  },
]

export const heroStats = [
  { icon: 'Users', value: '12,487+', label: 'Codeurs actifs' },
  { icon: 'Code2', value: '892+', label: 'Projets disponibles' },
  { icon: 'TrendingUp', value: '21', label: 'Niveaux (0.00 → 21.00)' },
  { icon: 'Clock', value: '3,245h', label: 'Heures de code' },
  { icon: 'Flag', value: '42', label: 'Coalitions actives' },
]

export const heroPerks = [
  { icon: 'Gift', label: '100% Gratuit' },
  { icon: 'Users', label: 'Apprentissage par les pairs' },
  { icon: 'Code2', label: 'Projets réels' },
  { icon: 'Ban', label: 'Sans profs' },
]

/* ------------------------------------------------------------------ */
/* Projects                                                            */
/* ------------------------------------------------------------------ */

export const projects = [
  {
    id: 'p1',
    slug: 'get_next_line',
    name: 'get_next_line',
    level: 'Niveau 1',
    lang: 'C',
    langColor: '#3B9EFF',
    desc: 'Lis une ligne depuis un file descriptor, sans jamais perdre le fil.',
    tags: ['Solo', 'I/O', 'Buffer'],
    status: 'done',
    score: 100,
    xp: 1200,
    duration: '1 sem.',
    difficulty: 2,
  },
  {
    id: 'p2',
    slug: 'ft_printf',
    name: 'ft_printf',
    level: 'Niveau 2',
    lang: 'C',
    langColor: '#3B9EFF',
    desc: 'Recode la fonction variadique la plus utilisée de la libc.',
    tags: ['Solo', 'Variadic', 'Parsing'],
    status: 'done',
    score: 115,
    bonus: true,
    xp: 1500,
    duration: '2 sem.',
    difficulty: 3,
  },
  {
    id: 'p3',
    slug: 'minishell',
    name: 'minishell',
    level: 'Niveau 4',
    lang: 'C',
    langColor: '#3B9EFF',
    desc: "Écris ton propre shell : parsing, pipes, redirections, builtins et signaux.",
    tags: ['Duo', 'Unix', 'Parsing'],
    status: 'progress',
    progress: 68,
    xp: 3200,
    duration: '4 sem.',
    difficulty: 5,
  },
  {
    id: 'p4',
    slug: 'philosophers',
    name: 'philosophers',
    level: 'Niveau 3',
    lang: 'C',
    langColor: '#3B9EFF',
    desc: 'Résous le problème des philosophes avec threads et mutex, sans data race.',
    tags: ['Solo', 'Threads', 'Concurrence'],
    status: 'failed',
    score: 42,
    retryIn: '2 j.',
    xp: 2100,
    duration: '2 sem.',
    difficulty: 4,
  },
  {
    id: 'p5',
    slug: 'netpractice',
    name: 'netpractice',
    level: 'Niveau 4',
    lang: 'Réseau',
    langColor: '#2ECC71',
    desc: 'Configure des réseaux TCP/IP et comprends enfin le masque de sous-réseau.',
    tags: ['Solo', 'Réseau'],
    status: 'done',
    score: 100,
    xp: 1100,
    duration: '3 j.',
    difficulty: 2,
  },
  {
    id: 'p6',
    slug: 'cub3d',
    name: 'cub3d',
    level: 'Niveau 5',
    lang: 'C',
    langColor: '#3B9EFF',
    desc: 'Un moteur de rendu 3D en raycasting, inspiré du légendaire Wolfenstein 3D.',
    tags: ['Duo', 'Graphique', 'Maths'],
    status: 'available',
    xp: 3600,
    duration: '4 sem.',
    difficulty: 5,
  },
  {
    id: 'p7',
    slug: 'webserv',
    name: 'webserv',
    level: 'Niveau 6',
    lang: 'C++',
    langColor: '#F26FA4',
    desc: 'Implémente un serveur HTTP/1.1 conforme, non-bloquant, façon NGINX.',
    tags: ['Trio', 'Réseau', 'HTTP'],
    status: 'locked',
    requires: 'minishell',
    xp: 4200,
    duration: '5 sem.',
    difficulty: 5,
  },
  {
    id: 'p8',
    slug: 'inception',
    name: 'inception',
    level: 'Niveau 6',
    lang: 'Docker',
    langColor: '#3B9EFF',
    desc: 'Orchestre une infrastructure multi-conteneurs avec Docker Compose.',
    tags: ['Solo', 'DevOps', 'Docker'],
    status: 'locked',
    requires: 'webserv',
    xp: 2800,
    duration: '3 sem.',
    difficulty: 4,
  },
  {
    id: 'p9',
    slug: 'ft_transcendence',
    name: 'ft_transcendence',
    level: 'Niveau 8',
    lang: 'Web',
    langColor: '#F5B942',
    desc: 'Le projet final : une SPA temps réel avec un Pong multijoueur en ligne.',
    tags: ['Groupe', 'Fullstack', 'WebSocket'],
    status: 'locked',
    requires: 'inception',
    xp: 8000,
    duration: '8 sem.',
    difficulty: 5,
  },
]

export const projectStatusMap = {
  done: { label: 'Terminé', tone: 'ok', icon: 'CheckCircle2' },
  progress: { label: 'En cours', tone: 'brand', icon: 'Loader' },
  failed: { label: 'Échoué', tone: 'danger', icon: 'XCircle' },
  available: { label: 'Disponible', tone: 'info', icon: 'Unlock' },
  locked: { label: 'Verrouillé', tone: 'muted', icon: 'Lock' },
}

/* ------------------------------------------------------------------ */
/* Dashboard                                                           */
/* ------------------------------------------------------------------ */

export const dashboardStats = [
  { key: 'xp', label: 'XP', value: '24,780', sub: 'Total', icon: 'Zap', delta: '+1,240' },
  { key: 'done', label: 'Projets terminés', value: '38', sub: 'sur 92', icon: 'CheckCircle2', delta: '+2' },
  { key: 'cp', label: 'Correction Points', value: '1,250', sub: '+80 cette sem.', icon: 'Users', delta: '+80' },
  { key: 'wallet', label: 'Valeur de compte', value: '2,450', sub: '4 jetons', icon: 'Coins', delta: '+150' },
]

export const recentActivity = [
  { id: 1, project: 'get_next_line', kind: 'Moulinette réussie', score: '100', tone: 'ok', time: 'il y a 2 h' },
  { id: 2, project: 'ft_printf', kind: 'Peer Review validé', score: '115', tone: 'ok', time: 'il y a 5 h' },
  { id: 3, project: 'minishell', kind: 'Soumission en attente', score: 'En cours', tone: 'brand', time: 'hier' },
  { id: 4, project: 'netpractice', kind: 'Niveau validé', score: '100', tone: 'ok', time: 'il y a 3 j.' },
  { id: 5, project: 'philosophers', kind: 'Moulinette échouée', score: '42', tone: 'danger', time: 'il y a 4 j.' },
]

export const weeklyActivity = [
  { day: 'Lun', value: 42 },
  { day: 'Mar', value: 68 },
  { day: 'Mer', value: 95 },
  { day: 'Jeu', value: 54 },
  { day: 'Ven', value: 78 },
  { day: 'Sam', value: 88 },
  { day: 'Dim', value: 31 },
]

export const dailyMission = {
  title: 'Reverse a linked list',
  difficulty: 3,
  time: '~30 min',
  reward: 120,
  skill: 'Structures de données',
}

export const upcomingSlots = [
  { id: 1, project: 'minishell', peer: 'nour_dev', time: 'Aujourd’hui 16:30', role: 'Corrigé' },
  { id: 2, project: 'ft_printf', peer: 'skhalifa', time: 'Demain 10:00', role: 'Correcteur' },
]

/* ------------------------------------------------------------------ */
/* Leaderboard                                                         */
/* ------------------------------------------------------------------ */

export const leaderboard = [
  { rank: 1, user: 'BlackHoleSurvivor', name: 'Yassine T.', level: 11.36, xp: '58,420', projects: 64, accuracy: 93, coalition: 'The Phoenix', avatar: 'https://i.pravatar.cc/80?img=12' },
  { rank: 2, user: 'chaimacoder', name: 'Chaima B.', level: 10.87, xp: '51,110', projects: 60, accuracy: 91, coalition: 'Neon Wolves', avatar: 'https://i.pravatar.cc/80?img=45' },
  { rank: 3, user: 'mehdi42', name: 'Mehdi K.', level: 9.94, xp: '46,230', projects: 52, accuracy: 90, coalition: 'Data Vipers', avatar: 'https://i.pravatar.cc/80?img=33' },
  { rank: 4, user: 'abdeljalil', name: 'Abdeljalil B.', level: 6.42, xp: '24,780', projects: 38, accuracy: 81, coalition: 'The Phoenix', avatar: 'https://i.pravatar.cc/160?img=13', me: true },
  { rank: 5, user: 'ines_dev', name: 'Ines S.', level: 6.36, xp: '23,940', projects: 37, accuracy: 89, coalition: 'Neon Wolves', avatar: 'https://i.pravatar.cc/80?img=47' },
  { rank: 6, user: 'skhalifa', name: 'Sarra K.', level: 6.02, xp: '22,180', projects: 35, accuracy: 86, coalition: 'Sand Foxes', avatar: 'https://i.pravatar.cc/80?img=26' },
  { rank: 7, user: 'nour_dev', name: 'Nour H.', level: 5.88, xp: '21,050', projects: 33, accuracy: 84, coalition: 'Data Vipers', avatar: 'https://i.pravatar.cc/80?img=32' },
  { rank: 8, user: 'oussama_c', name: 'Oussama R.', level: 5.41, xp: '19,620', projects: 31, accuracy: 79, coalition: 'The Phoenix', avatar: 'https://i.pravatar.cc/80?img=53' },
]

export const coalitions = [
  { id: 1, name: 'The Phoenix', color: '#F8851F', points: 7286, members: 312, wins: 14, trend: '+320', motto: 'Renaître de chaque segfault.' },
  { id: 2, name: 'Neon Wolves', color: '#3B9EFF', points: 6941, members: 298, wins: 11, trend: '+180', motto: 'La meute compile ensemble.' },
  { id: 3, name: 'Data Vipers', color: '#2ECC71', points: 6402, members: 305, wins: 9, trend: '+95', motto: 'Silencieux, précis, mortels.' },
  { id: 4, name: 'Sand Foxes', color: '#F5B942', points: 5877, members: 281, wins: 8, trend: '+60', motto: 'Rusés dans le désert du code.' },
]

/* ------------------------------------------------------------------ */
/* Rooms / Community                                                   */
/* ------------------------------------------------------------------ */

export const roomTypes = [
  { key: 'study', label: 'Study Room', icon: 'BookOpen', color: '#3B9EFF' },
  { key: 'correction', label: 'Correction Room', icon: 'ClipboardCheck', color: '#F8851F' },
  { key: 'pair', label: 'Pair Programming', icon: 'Users', color: '#2ECC71' },
  { key: 'competition', label: 'Competition Room', icon: 'Trophy', color: '#F5B942' },
  { key: 'mentor', label: 'Mentor Room', icon: 'GraduationCap', color: '#B37BFF' },
  { key: 'live', label: 'Live Coding', icon: 'Radio', color: '#E5484D' },
]

export const rooms = [
  { id: 'r1', name: 'Correction Room 1', type: 'correction', project: 'minishell', members: 2, capacity: 2, live: true, host: 'nour_dev', tags: ['C', 'Peer Review'] },
  { id: 'r2', name: 'Pointeurs & Mémoire', type: 'study', project: 'get_next_line', members: 6, capacity: 10, live: true, host: 'mehdi42', tags: ['C', 'Débutant'] },
  { id: 'r3', name: 'Duo cub3d', type: 'pair', project: 'cub3d', members: 2, capacity: 2, live: true, host: 'ines_dev', tags: ['Raycasting'] },
  { id: 'r4', name: 'Coalition War — Sprint 48h', type: 'competition', project: 'Algo Dojo', members: 24, capacity: 40, live: true, host: 'system', tags: ['Compétition'] },
  { id: 'r5', name: 'Office Hours — Systèmes', type: 'mentor', project: 'Mentorat', members: 9, capacity: 20, live: false, host: 'BlackHoleSurvivor', tags: ['Mentor', 'Level 15+'] },
  { id: 'r6', name: 'Live: Build a Web Server', type: 'live', project: 'webserv', members: 118, capacity: 500, live: true, host: 'chaimacoder', tags: ['Stream'] },
]

export const chatChannels = [
  { group: 'ROOT 404', items: [{ name: 'annonces', icon: 'Megaphone' }, { name: 'règles', icon: 'Scale' }, { name: 'général', icon: 'Hash' }] },
  { group: 'Cursus', items: [{ name: 'c-piscine', icon: 'Hash' }, { name: 'algorithmes', icon: 'Hash' }, { name: 'minishell', icon: 'Hash' }, { name: 'philosophers', icon: 'Hash' }] },
  { group: 'Coalitions', items: [{ name: 'the-phoenix', icon: 'Flame' }, { name: 'coalition-wars', icon: 'Swords' }] },
  { group: 'Vocal', items: [{ name: 'Salon 1', icon: 'Volume2' }, { name: 'Pair Programming', icon: 'Volume2' }] },
]

export const chatMessages = [
  { id: 1, user: 'nour_dev', avatar: 'https://i.pravatar.cc/64?img=32', time: '14:02', text: 'Salut ! On commence la correction de minishell dans 5 min ?' },
  { id: 2, user: 'abdeljalil', avatar: 'https://i.pravatar.cc/160?img=13', time: '14:03', text: 'Yes, je pousse mon dernier commit et je rejoins le vocal.', me: true },
  { id: 3, user: 'nour_dev', avatar: 'https://i.pravatar.cc/64?img=32', time: '14:04', text: 'Parfait. Prépare la checklist, je vais tester les heredocs en premier.' },
  { id: 4, user: 'mehdi42', avatar: 'https://i.pravatar.cc/64?img=33', time: '14:06', text: 'Attention aux leaks sur les pipes, ça m’a coûté 20 points la semaine dernière.' },
  { id: 5, user: 'abdeljalil', avatar: 'https://i.pravatar.cc/160?img=13', time: '14:07', text: 'Noté 🙏 valgrind est déjà lancé.', me: true },
]

export const roomMembers = [
  { name: 'nour_dev', status: 'online', avatar: 'https://i.pravatar.cc/64?img=32', role: 'Correcteur' },
  { name: 'abdeljalil', status: 'online', avatar: 'https://i.pravatar.cc/160?img=13', role: 'Corrigé' },
  { name: 'mehdi42', status: 'online', avatar: 'https://i.pravatar.cc/64?img=33', role: 'Observateur' },
  { name: 'ines_dev', status: 'idle', avatar: 'https://i.pravatar.cc/64?img=47', role: 'Observateur' },
  { name: 'skhalifa', status: 'offline', avatar: 'https://i.pravatar.cc/64?img=26', role: 'Observateur' },
]

/* ------------------------------------------------------------------ */
/* Workspace / Editor                                                  */
/* ------------------------------------------------------------------ */

export const fileTree = [
  {
    name: 'minishell', type: 'folder', open: true, children: [
      {
        name: 'src', type: 'folder', open: true, children: [
          { name: 'minishell.c', type: 'file', lang: 'c', active: true },
          { name: 'parser.c', type: 'file', lang: 'c' },
          { name: 'exec.c', type: 'file', lang: 'c' },
          { name: 'builtins.c', type: 'file', lang: 'c' },
        ],
      },
      {
        name: 'includes', type: 'folder', open: true, children: [
          { name: 'minishell.h', type: 'file', lang: 'h' },
          { name: 'parser.h', type: 'file', lang: 'h' },
        ],
      },
      { name: 'Makefile', type: 'file', lang: 'make' },
      { name: 'README.md', type: 'file', lang: 'md' },
    ],
  },
]

export const sampleCode = `#include "minishell.h"

int	main(int ac, char **av, char **envp)
{
	t_shell	*sh;
	char	*line;

	sh = init_shell(envp);
	if (!sh)
		return (1);
	while (1)
	{
		line = readline(PROMPT);
		if (!line)
			break ;
		add_history(line);
		parse_and_execute(sh, line);
		free(line);
	}
	free_shell(sh);
	return (0);
}
`

export const terminalLines = [
  { t: 'cmd', v: '$ make -j4' },
  { t: 'out', v: 'cc -Wall -Wextra -Werror -Iincludes -c src/minishell.c -o obj/minishell.o' },
  { t: 'out', v: 'cc -Wall -Wextra -Werror -Iincludes -c src/parser.c    -o obj/parser.o' },
  { t: 'out', v: 'cc -Wall -Wextra -Werror -Iincludes -c src/exec.c      -o obj/exec.o' },
  { t: 'out', v: 'cc -Wall -Wextra -Werror -Iincludes -c src/builtins.c  -o obj/builtins.o' },
  { t: 'ok', v: 'cc obj/*.o -lreadline -o minishell   ✓' },
  { t: 'cmd', v: '$ ./minishell' },
  { t: 'out', v: 'minishell$ echo "hello ROOT 404"' },
  { t: 'out', v: 'hello ROOT 404' },
  { t: 'cmd', v: 'minishell$ ' },
]

export const moulinetteTests = [
  { name: 'Norminette', status: 'pass', detail: 'OK' },
  { name: 'Makefile (rules & flags)', status: 'pass', detail: 'OK' },
  { name: 'Fuites mémoire (valgrind)', status: 'pass', detail: '0 bytes lost' },
  { name: 'Builtins (echo, cd, pwd, env)', status: 'pass', detail: 'OK' },
  { name: 'Pipes & redirections', status: 'pass', detail: '38/38' },
  { name: 'Heredoc multi-niveaux', status: 'warn', detail: '2 cas limites' },
  { name: 'Signaux (SIGINT / SIGQUIT)', status: 'fail', detail: 'Ctrl-\\ non géré' },
]

export const aiCodeReview = {
  metrics: [
    { label: 'Correctness', value: 94 },
    { label: 'Memory Safety', value: 88 },
    { label: 'Code Quality', value: 81 },
    { label: 'Complexity', value: 73 },
    { label: 'Readability', value: 90 },
  ],
  notes: [
    { tone: 'warn', text: 'La fonction `parse_and_execute` est trop complexe (complexité cyclomatique 17).' },
    { tone: 'info', text: 'Concept suggéré : Separation of Concerns — sépare le parsing de l’exécution.' },
  ],
}

/* ------------------------------------------------------------------ */
/* AI Mentor                                                           */
/* ------------------------------------------------------------------ */

export const aiConversation = [
  {
    role: 'ai',
    text: "Salut Abdeljalil 👋 J'ai analysé ta dernière soumission de `minishell`. Je ne vais pas te donner la solution — mais je peux t'aider à la trouver. Par quoi veux-tu commencer ?",
    chips: ['Comprendre mon erreur', 'Expliquer un concept', 'Me donner un indice'],
  },
  {
    role: 'user',
    text: "Mon shell segfault quand je fais `cat | cat | ls`. Je ne comprends pas pourquoi.",
  },
  {
    role: 'ai',
    text: "Bonne observation — ce cas enchaîne trois processus. Avant de plonger dans le code, réponds-moi :",
    list: [
      'Combien de pipes crées-tu pour 3 commandes ?',
      'Que deviennent les descripteurs dans le processus parent après le fork ?',
      'Est-ce que chaque enfant ferme bien les extrémités qu’il n’utilise pas ?',
    ],
    footer: "Un segfault ici vient souvent d'un `close()` manquant ou d'un tableau de pipes mal indexé.",
  },
]

export const aiLevels = [
  { n: 1, label: 'Hint initial' },
  { n: 2, label: 'Question socratique' },
  { n: 3, label: 'Explication du concept' },
  { n: 4, label: 'Exemple simplifié' },
  { n: 5, label: 'Ressources & exercices' },
]

/* ------------------------------------------------------------------ */
/* Skills / Journey / Analytics                                        */
/* ------------------------------------------------------------------ */

export const skillGraph = [
  {
    group: 'C', color: '#3B9EFF', skills: [
      { name: 'Variables', value: 95 },
      { name: 'Pointers', value: 62 },
      { name: 'Memory', value: 41 },
      { name: 'Structs', value: 78 },
      { name: 'Functions', value: 91 },
    ],
  },
  {
    group: 'Algorithms', color: '#F8851F', skills: [
      { name: 'Sorting', value: 82 },
      { name: 'Recursion', value: 48 },
      { name: 'Complexity', value: 37 },
      { name: 'Graphs', value: 15 },
    ],
  },
  {
    group: 'Systems', color: '#2ECC71', skills: [
      { name: 'Processes', value: 71 },
      { name: 'Threads', value: 44 },
      { name: 'Signals', value: 58 },
      { name: 'Sockets', value: 29 },
    ],
  },
  {
    group: 'Tooling', color: '#B37BFF', skills: [
      { name: 'Git', value: 88 },
      { name: 'Docker', value: 67 },
      { name: 'Makefile', value: 84 },
      { name: 'Valgrind', value: 55 },
    ],
  },
]

export const journeyStages = [
  { id: 0, title: 'LEVEL 00 — Piscine', status: 'done', projects: 12, skills: ['Shell', 'Logique', 'C basics'], progress: 100 },
  { id: 1, title: 'C / Programming', status: 'done', projects: 8, skills: ['Pointeurs', 'Structs', 'Libc'], progress: 100 },
  { id: 2, title: 'Algorithms', status: 'current', projects: 6, skills: ['Tri', 'Récursion', 'Complexité'], progress: 62 },
  { id: 3, title: 'Memory / Systems', status: 'next', projects: 7, skills: ['Threads', 'Processus', 'Signaux'], progress: 0 },
  { id: 4, title: 'Advanced', status: 'locked', projects: 9, skills: ['Réseau', 'Graphique', 'C++'], progress: 0 },
  { id: 5, title: 'Final Project', status: 'locked', projects: 1, skills: ['Fullstack', 'Temps réel'], progress: 0 },
]

export const analytics = {
  velocity: 78,
  consistency: 91,
  tolerance: [
    { label: 'Easy', value: 100 },
    { label: 'Medium', value: 88 },
    { label: 'Hard', value: 61 },
    { label: 'Extreme', value: 28 },
  ],
  insight:
    "Tu résous les exercices d'algorithmie rapidement, mais tu passes 2,4× plus de temps à déboguer les problèmes liés à la mémoire.",
  forecast: '14 mars 2027',
  timeToSolve: [
    { label: 'Algo', you: 3.2, avg: 4.1 },
    { label: 'Mémoire', you: 7.8, avg: 4.6 },
    { label: 'Réseau', you: 5.1, avg: 5.4 },
    { label: 'Parsing', you: 4.4, avg: 5.0 },
    { label: 'Threads', you: 6.9, avg: 5.2 },
  ],
}

export const reputation = [
  { label: 'Code Quality', value: 92 },
  { label: 'Peer Reviewer', value: 87 },
  { label: 'Community', value: 78 },
  { label: 'Mentorship', value: 91 },
  { label: 'Reliability', value: 95 },
]

export const integrityScore = {
  total: 96,
  rows: [
    { label: 'Code Similarity', value: '2%', tone: 'ok' },
    { label: 'Typing Pattern', value: 'Normal', tone: 'ok' },
    { label: 'Submission Pattern', value: 'Normal', tone: 'ok' },
    { label: 'AI Dependency', value: 'Low', tone: 'ok' },
    { label: 'Peer Review', value: 'Valid', tone: 'ok' },
  ],
}

export const badges = [
  { name: 'Top 5%', icon: 'Trophy', tier: 'gold' },
  { name: '87 Day Streak', icon: 'Flame', tier: 'gold' },
  { name: 'Trusted Reviewer', icon: 'ShieldCheck', tier: 'silver' },
  { name: 'Night Owl', icon: 'Moon', tier: 'bronze' },
  { name: 'Zero Leaks', icon: 'Droplet', tier: 'silver' },
  { name: 'Piscine Survivor', icon: 'Waves', tier: 'gold' },
  { name: 'Helper x50', icon: 'HeartHandshake', tier: 'bronze' },
  { name: 'Norm Master', icon: 'Ruler', tier: 'silver' },
]

/* 53 weeks × 7 days deterministic heatmap */
export const heatmap = Array.from({ length: 53 * 7 }, (_, i) => {
  const seed = (i * 2654435761) % 4294967296
  const r = (seed / 4294967296 + Math.sin(i * 0.7) * 0.3 + 0.2) % 1
  return r < 0.32 ? 0 : r < 0.5 ? 1 : r < 0.7 ? 2 : r < 0.88 ? 3 : 4
})

/* ------------------------------------------------------------------ */
/* Piscine                                                             */
/* ------------------------------------------------------------------ */

export const piscineDays = Array.from({ length: 28 }, (_, i) => {
  const d = i + 1
  const status = d < 12 ? 'done' : d === 12 ? 'today' : 'locked'
  return {
    day: d,
    title: `Day ${String(d).padStart(2, '0')}`,
    topic: ['Shell', 'Variables', 'Boucles', 'Pointeurs', 'Chaînes', 'Structs', 'Rush'][i % 7],
    status,
    score: status === 'done' ? 60 + ((i * 37) % 41) : null,
    isRush: d % 7 === 0,
  }
})

export const piscineStats = [
  { label: 'Jour actuel', value: '12 / 28', icon: 'CalendarDays' },
  { label: 'Exercices validés', value: '84', icon: 'CheckCircle2' },
  { label: 'Consistency Score', value: '91%', icon: 'Activity' },
  { label: 'Rang Piscine', value: '#17', icon: 'Trophy' },
]

/* ------------------------------------------------------------------ */
/* Arena                                                               */
/* ------------------------------------------------------------------ */

export const arenaModes = [
  { key: '1v1', name: '1v1 Coding Battle', desc: 'Duel direct sur un même problème. Le plus rapide gagne.', icon: 'Swords', players: '2', time: '15 min' },
  { key: 'team', name: 'Team Battle', desc: 'Trois contre trois, score cumulé de la coalition.', icon: 'Users', players: '3v3', time: '45 min' },
  { key: 'speed', name: 'Speed Coding', desc: 'Le maximum de problèmes en un minimum de temps.', icon: 'Timer', players: '∞', time: '20 min' },
  { key: 'algo', name: 'Algorithm Duel', desc: 'Meilleure complexité gagnante, pas la plus rapide à écrire.', icon: 'GitBranch', players: '2', time: '30 min' },
  { key: 'debug', name: 'Debugging Battle', desc: 'Un code cassé, sept bugs, un chronomètre.', icon: 'Bug', players: '2', time: '12 min' },
]

export const arenaLive = [
  { id: 1, a: 'mehdi42', b: 'ines_dev', problem: 'Binary Search', time: '07:41', viewers: 128 },
  { id: 2, a: 'chaimacoder', b: 'skhalifa', problem: 'LRU Cache', time: '11:05', viewers: 86 },
  { id: 3, a: 'nour_dev', b: 'oussama_c', problem: 'Merge Intervals', time: '02:18', viewers: 41 },
]

/* ------------------------------------------------------------------ */
/* Marketing content                                                   */
/* ------------------------------------------------------------------ */

export const pathways = [
  { name: 'Common Core', level: '0.00 → 10.00', projects: 17, weeks: 52, desc: 'Le tronc commun : C, algorithmie, systèmes Unix, réseau et graphique.', icon: 'Layers', color: '#F8851F' },
  { name: 'Web & Fullstack', level: '6.00 → 14.00', projects: 12, weeks: 24, desc: 'Du serveur HTTP maison aux SPA temps réel avec WebSockets.', icon: 'Globe', color: '#3B9EFF' },
  { name: 'AI / ML Bootcamp', level: '8.00 → 16.00', projects: 10, weeks: 20, desc: 'De la régression linéaire au Mini-LLM, en Python pur puis PyTorch.', icon: 'Brain', color: '#B37BFF' },
  { name: 'Security & CTF', level: '7.00 → 15.00', projects: 14, weeks: 18, desc: 'Web, crypto et reverse engineering en Capture The Flag.', icon: 'ShieldAlert', color: '#E5484D' },
  { name: 'DevOps & Cloud', level: '9.00 → 17.00', projects: 8, weeks: 16, desc: 'Docker, orchestration, CI/CD et infrastructure as code.', icon: 'Container', color: '#2ECC71' },
  { name: 'System Design Labs', level: '10.00 → 18.00', projects: 9, weeks: 14, desc: 'Load balancing, caching et microservices sur schémas interactifs.', icon: 'Network', color: '#F5B942' },
]

export const howItWorks = [
  { step: '01', title: 'Ouvre un projet', text: 'Choisis un sujet dans ton parcours adaptatif et lis le cahier des charges.', icon: 'FolderOpen' },
  { step: '02', title: 'Code dans le sandbox', text: 'Un conteneur Ubuntu isolé, identique pour tous, sans triche possible.', icon: 'Terminal' },
  { step: '03', title: 'Passe la Moulinette', text: 'Norme, fuites mémoire et cas de tests vérifiés automatiquement.', icon: 'Cpu' },
  { step: '04', title: 'Peer Review', text: 'Un pair te corrige en visio avec une checklist générée par le système.', icon: 'Users' },
  { step: '05', title: 'Gagne XP & niveau', text: 'Ton niveau progresse de 0.00 à 21.00 et débloque de nouveaux projets.', icon: 'TrendingUp' },
  { step: '06', title: 'Construis ton profil', text: 'Portfolio public vérifiable, partagé avec les entreprises partenaires.', icon: 'BadgeCheck' },
]

export const testimonials = [
  { name: 'Yassine Trabelsi', role: 'Backend Engineer @ Instadeep', avatar: 'https://i.pravatar.cc/96?img=12', text: "Six mois de ROOT 404 m'ont appris plus que trois ans de cours magistraux. La Moulinette est impitoyable, et c'est exactement ce qu'il fallait." },
  { name: 'Chaima Ben Ali', role: 'SRE @ Talan Tunisie', avatar: 'https://i.pravatar.cc/96?img=45', text: "Le peer review change tout : expliquer son code à quelqu'un d'autre, c'est là qu'on comprend vraiment ce qu'on a écrit." },
  { name: 'Mehdi Karray', role: 'Étudiant, Level 9.94', avatar: 'https://i.pravatar.cc/96?img=33', text: "La coalition m'a donné une raison de me lever à 6h. On code, on s'engueule sur les normes, on gagne des Wars ensemble." },
]

export const faqs = [
  { q: 'Faut-il un diplôme ou de l’expérience pour rejoindre ?', a: "Non. Aucun prérequis académique. Le seul filtre est la Piscine : quatre semaines intensives où l'on évalue ta capacité à apprendre par toi-même, pas ce que tu sais déjà." },
  { q: 'La plateforme est-elle vraiment gratuite ?', a: "Oui, 100 % gratuite pour les étudiants. ROOT 404 est financée par ses entreprises partenaires via la bourse d'emploi, jamais par les apprenants." },
  { q: 'Combien de temps par semaine faut-il investir ?', a: "Pendant la Piscine, compte 50 à 60 heures par semaine. Ensuite, le rythme est libre — mais le système Black Hole exige une progression minimale pour garder ta place." },
  { q: 'Qu’est-ce que le Black Hole exactement ?', a: "Un compte à rebours de survie. Chaque parcours a une durée cible ; sans progression suffisante, tu passes en zone d'avertissement, puis ton compte est gelé et ta place redistribuée." },
  { q: 'Comment fonctionne l’assistant IA ?', a: "Il est bridé volontairement : il ne donne jamais la solution finale. Il pose des questions socratiques, explique des concepts et détecte tes lacunes pour te proposer des micro-exercices." },
  { q: 'Mon code est-il exécuté en sécurité ?', a: "Chaque soumission tourne dans un conteneur Docker isolé, sans accès réseau, avec des limites strictes sur le CPU et la RAM. Rien ne sort du sandbox." },
]

export const blogPosts = [
  { id: 1, title: 'Pourquoi nous avons supprimé les professeurs', cat: 'Pédagogie', date: '18 août 2026', read: '6 min', excerpt: "L'apprentissage par les pairs n'est pas une économie de moyens : c'est un choix pédagogique radical. Voici les données de notre première promotion.", img: 'linear-gradient(135deg,#F8851F22,#04090E)' },
  { id: 2, title: 'Anatomie de notre Moulinette', cat: 'Ingénierie', date: '02 août 2026', read: '11 min', excerpt: 'Comment nous exécutons 40 000 soumissions par jour dans des conteneurs éphémères sans jamais exposer l’hôte.', img: 'linear-gradient(135deg,#3B9EFF22,#04090E)' },
  { id: 3, title: 'Le Skill Graph, ou la fin de la note unique', cat: 'Produit', date: '21 juillet 2026', read: '8 min', excerpt: 'Un niveau de 6.42 ne dit rien de tes lacunes en gestion mémoire. Le Skill Graph, si.', img: 'linear-gradient(135deg,#2ECC7122,#04090E)' },
]

export const timeline = [
  { year: '2024', title: 'L’idée', text: "Trois développeurs tunisiens frustrés par l'écart entre l'université et le marché." },
  { year: '2025', title: 'Premier prototype', text: 'Moulinette maison, 40 étudiants, une Piscine improvisée dans un coworking à Ariana.' },
  { year: '2026', title: 'ROOT 404', text: 'Ouverture publique, 12 487 codeurs actifs, 42 coalitions et trois campus.' },
  { year: '2027', title: 'Multi-campus', text: 'Sfax, Sousse et un classement national inter-campus.' },
]

export const values = [
  { icon: 'Users', title: 'Peer-to-peer avant tout', text: "Personne ne t'enseigne. Tout le monde t'aide. La différence est fondamentale." },
  { icon: 'ShieldCheck', title: 'Mérite vérifiable', text: "Pas de Level achetable, pas de score négociable. Ton profil est un fait, pas une déclaration." },
  { icon: 'Brain', title: 'L’IA comme guide', text: "Elle pose des questions, jamais des réponses. Le raccourci n'apprend rien." },
  { icon: 'Globe', title: 'Ancré en Tunisie', text: 'Contenu trilingue, entreprises locales, communauté qui se rencontre en vrai.' },
]
