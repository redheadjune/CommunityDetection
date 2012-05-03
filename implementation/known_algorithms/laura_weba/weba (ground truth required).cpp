#include <cstdio>
#include <cstdlib>
#include <string>
#include <cmath>
#include <vector>
#include <set>
#include <map>
#include <algorithm>
#include <ctime>

using namespace std;

typedef vector<int> VI;
typedef set<int> SI;
#define LENGTH(A) ((int)A.length())
typedef pair<int,int> ipair;
#define MP(A,B) make_pair(A,B)
#define SIZE(A) ((int)A.size())
#define ASSERT(X) {if (!(X)) { printf("ERROR   LINE %d\n",__LINE__); exit(0); }}
template<class T> void ckmin(T &a,T b) { if (b<a) a=b; }
template<class T> void ckmax(T &a,T b) { if (b>a) a=b; }

int n, m, *edge_ep, *degree, **g, max_degree;


void trim(string &s)
{
	while (LENGTH(s) > 0 && s[0] <= 32) s = s.substr(1);
	while (LENGTH(s) > 0 && s[LENGTH(s) - 1] <= 32) s = s.substr(0, LENGTH(s) - 1);
}

void load_graph(string filename)
{
	FILE *f = fopen(filename.c_str(), "r");
	fscanf(f, "%d%d", &n, &m);
	edge_ep = new int[m + m];
	for (int i = 0; i < m + m; ++i)
		fscanf(f, "%d", &edge_ep[i]);
	fclose(f);
	for (int i = 0; i < m + m; ++i)
		ASSERT(edge_ep[i] != edge_ep[i ^ 1]);
	degree = new int[n];
	for (int i = 0; i < n; ++i)
		degree[i] = 0;
	for (int i = 0; i < m + m; ++i)
		++degree[edge_ep[i]];
	g = new int* [n];
	for (int i = 0; i < n; ++i)
		g[i] = new int[degree[i]];
	for (int i = 0; i < n; ++i)
		degree[i] = 0;
	for (int i = 0; i < m + m; ++i)
		g[edge_ep[i]][degree[edge_ep[i]]++] = edge_ep[i ^ 1];
	max_degree = 0;
	for (int i = 0; i < n; ++i)
		ckmax(max_degree, degree[i]);
}

VI refine(const int csize, const VI &init_set)
{
	VI results;
	vector<ipair> q;
	for (int i = 0; i < SIZE(init_set); ++i)
		q.push_back(MP(-degree[init_set[i]], init_set[i]));
	sort(q.begin(), q.end());
	for (int i = 0; i < csize; ++i)
		results.push_back(q[i].second);
	return results;
}

const int C = 5;

bool is_initialized = false;
VI *buckets[C + 1];
int *position;

void buckets_ready(int e[], int c[])
{
	if (!is_initialized)
	{
		is_initialized = true;
		for (int k = 0; k <= C; ++k)
			buckets[k] = new VI[max_degree * C + 1];
		position = new int[n];
	}
	for (int k = 0; k <= C; ++k)
		for (int i = 0; i <= max_degree; ++i)
			buckets[k][i].clear();
	for (int i = 0; i < n; ++i)
	{
		int e0 = e[i];
		int c0 = c[i];
		position[i] = SIZE(buckets[c0][e0]);
		buckets[c0][e0].push_back(i);
	}
}

void erase(int e[], int c[], int key)
{
	int e0 = e[key];
	int c0 = c[key];
	VI &old = buckets[c0][e0];
	int pos = position[key];
	if (pos < SIZE(old))
	{
		old[pos] = old[SIZE(old) - 1];
		position[old[pos]] = pos;
	}
	old.pop_back();
}

void add(int e[], int c[], int key)
{
	int e0 = e[key];
	int c0 = c[key];
	VI &old = buckets[c0][e0];
	position[key] = SIZE(old);
	old.push_back(key);
}

int random(int n)
{
	return (n < 32768) ? (rand() % n) : ((((rand() & 32767) << 15) + (rand () & 32767)) % n);
}

VI greedy(const int csize, const VI &init_set)
{
	ASSERT(csize <= n);
	VI results = init_set;
	if (SIZE(init_set) > csize)
		results = refine(csize, init_set);
	ASSERT(SIZE(results) <= csize);
	int *c = new int[n];
	int *e = new int[n];
	for (int i = 0; i < n; ++i)
	{
		c[i] = 0;
		e[i] = 0;
	}
	for (int i = 0; i < SIZE(results); ++i)
	{
		int key = results[i];
		c[key] = 1;
		for (int j = 0; j < degree[key]; ++j)
			++e[g[key][j]];
	}
	buckets_ready(e, c);
	for (; SIZE(results) < csize; )
	{
		int e1 = max_degree;
		for (; buckets[0][e1].empty(); --e1);
		int key = buckets[0][e1][random(SIZE(buckets[0][e1]))];
		erase(e, c, key);
		results.push_back(key);
		c[key] = 1;
		for (int i = 0; i < degree[key]; ++i)
		{
			int other = g[key][i];
			if (c[other] == 0)
			{
				erase(e, c, other);
				++e[other];
				add(e, c, other);
			}
		}
	}
	delete[] c;
	delete[] e;
	sort(results.begin(), results.end());
	return results;
}


VI annealing(const int csize, const VI &init_set)
{
	ASSERT(csize <= n);
	VI beta_set = greedy(csize, init_set);
	ASSERT(SIZE(beta_set) == csize);
	int *c = new int[n];
	int *e = new int[n];
	int *r = new int[n];
	for (int i = 0; i < n; ++i)
	{
		c[i] = 0;
		e[i] = 0;
	}
	for (int i = 0; i < SIZE(beta_set); ++i)
	{
		int key = beta_set[i];
		c[key] = 1;
		for (int j = 0; j < degree[key]; ++j)
			++e[g[key][j]];
	}
	buckets_ready(e, c);
	for (int round = 0; 1; round++)
	{
		int e0 = max_degree;
		int e1 = 0;
		for (; buckets[0][e0].empty(); --e0);
		for (; buckets[1][e1].empty(); ++e1);
		if (e0 <= e1 + 1)
			break;
		int p0 = buckets[0][e0][random(SIZE(buckets[0][e0]))];
		int p1 = buckets[1][e1][random(SIZE(buckets[1][e1]))];
		ASSERT(c[p0] == 0 && c[p1] == 1);
		erase(e, c, p0);
		erase(e, c, p1);
		c[p0] = 1;
		c[p1] = 0;
		for (int step = 0; step < 2; ++step)
		{
			int key = (step == 0) ? p0 : p1;
			e[key] = 0;
			for (int i = 0; i < degree[key]; ++i)
			{
				int other = g[key][i];
				if (c[other])
					++e[key];
				if (other == p0 || other == p1)
					continue;
				erase(e, c, other);
				if (step == 0)
					++e[other];
				else
					--e[other];
				add(e, c, other);
			}
		}
/*
		for (int i = 0; i < n; ++i)
		{
			int exp = 0;
			for (int j = 0; j < degree[i]; ++j)
				if (c[g[i][j]] == 1)
					exp++;
			ASSERT(e[i] == exp);
		}
		for (int k = 0; k < 2; ++k)
			for (int i = 0; i <= max_degree; ++i)
				for (int j = 0; j < SIZE(buckets[k][i]); ++j)
				{
					int key = buckets[k][i][j];
					ASSERT(c[key] == k && e[key] == i);
				}
*/
		add(e, c, p0);
		add(e, c, p1);
	}
	VI results;
	for (int i = 0; i < n; ++i)
		if (c[i] == 1)
			results.push_back(i);
	delete[] r;
	delete[] c;
	delete[] e;
	return results;
}

VI annealing_improved(const int csize, const VI &init_set)
{
	ASSERT(csize <= n);
	VI beta_set = greedy(csize, init_set);
	ASSERT(SIZE(beta_set) == csize);
	int *c = new int[n];
	int *e = new int[n];
	int *r = new int[n];
	for (int i = 0; i < n; ++i)
	{
		c[i] = 0;
		e[i] = 0;
	}
	for (int i = 0; i < SIZE(beta_set); ++i)
	{
		int key = beta_set[i];
		c[key] = C;
		for (int j = 0; j < degree[key]; ++j)
			e[g[key][j]] += C;
	}
	buckets_ready(e, c);
	for (int round = 0; 1; round++)
	{
		int max_delta = 0;
		int max_p0 = -1, max_p1 = -1;
		int sw0[C + 1], sw1[C + 1];
		for (int e0 = 0; e0 <= C; ++e0)
		{
			int g = 0;
			for (; g <= max_degree * C && buckets[e0][g].empty(); ++g);
			if (g > max_degree * C)
				sw0[e0] = sw1[e0] = -1;
			else
			{
				sw0[e0] = g;
				for (g = max_degree * C; buckets[e0][g].empty(); --g);
				sw1[e0] = g;
			}
		}
		for (int e0 = 0; e0 < C; ++e0) if (sw0[e0] >= 0)
			for (int e1 = 1; e1 <= C; ++e1) if (sw0[e1] >= 0)
				if (sw1[e0] > sw0[e1])
				{
					int p0 = buckets[e0][sw1[e0]][random(SIZE(buckets[e0][sw1[e0]]))];
					int p1 = buckets[e1][sw0[e1]][random(SIZE(buckets[e1][sw0[e1]]))];
					bool exists = false;
					for (int i = 0; i < degree[p0]; ++i) if (g[p0][i] == p1) exists = true;
					int delta = min(C - e0, e1);
					if (exists)
						delta = min(delta, (sw1[e0] - sw0[e1]) / 2);
					if (delta > max_delta)
					{
						max_delta = delta;
						max_p0 = p0;
						max_p1 = p1;
					}
				}
		if (max_delta <= 0)
			break;
		int p0 = max_p0;
		int p1 = max_p1;
		ASSERT(c[p0] <= C - max_delta && c[p1] >= max_delta);
		erase(e, c, p0);
		erase(e, c, p1);
		c[p0] += max_delta;
		c[p1] -= max_delta;
		for (int step = 0; step < 2; ++step)
		{
			int key = (step == 0) ? p0 : p1;
			e[key] = 0;
			for (int i = 0; i < degree[key]; ++i)
			{
				int other = g[key][i];
				e[key] += c[other];
				if (other == p0 || other == p1)
					continue;
				erase(e, c, other);
				if (step == 0)
					e[other] += max_delta;
				else
					e[other] -= max_delta;
				add(e, c, other);
			}
		}
/*
		for (int i = 0; i < n; ++i)
		{
			int exp = 0;
			for (int j = 0; j < degree[i]; ++j)
				exp += c[g[i][j]];
			ASSERT(e[i] == exp);
		}
		for (int k = 0; k <= C; ++k)
			for (int i = 0; i <= max_degree * C; ++i)
				for (int j = 0; j < SIZE(buckets[k][i]); ++j)
				{
					int key = buckets[k][i][j];
					ASSERT(c[key] == k && e[key] == i);
				}
*/
		add(e, c, p0);
		add(e, c, p1);
	}
	VI results;
	for (int i = 0; i < n; ++i)
		if (c[i] == C)
			results.push_back(i);
	delete[] r;
	delete[] c;
	delete[] e;
	return results;
}

string *names;

void load_name(string filename)
{
	names = new string[n];
	FILE *f = fopen(filename.c_str(), "r");
	char *str = new char[1 << 20];
	while (1)
	{
		str[0] = 0;
		fgets(str, 1 << 20, f);
		if (str[0] == 0)
			break;
		int p = 0;
		for (; str[p] != ' '; p++);
		int id;
		sscanf(str, "%d", &id);
		names[id] = str + p + 1;
		trim(names[id]);
	}
	delete[] str;
	fclose(f);
}


ipair get_alpha_beta(VI s)
{
	ASSERT(SIZE(s) > 0 && SIZE(s) < n);
	bool *used = new bool[n];
	int *e = new int[n];
	for (int i = 0; i < n; ++i)
	{
		used[i] = false;
		e[i] = 0;
	}
	for (int i = 0; i < SIZE(s); ++i)
	{
		int key = s[i];
		used[key] = true;
		for (int j = 0; j < degree[key]; ++j)
			++e[g[key][j]];
	}
	int alpha = 0, beta = n + 1;
	for (int i = 0; i < n; ++i)
		if (used[i])
			ckmin(beta, e[i]);
		else
			ckmax(alpha, e[i]);
	delete[] e;
	delete[] used;
	return MP(alpha, beta);
}

VI load_community(string filename)
{
	VI results;
	FILE *f = fopen(filename.c_str(), "r");
	char *s = new char[1 << 20];
	while (1)
	{
		s[0] = 0;
		fgets(s, 1 << 20, f);
		if (s[0] == 0)
			break;
		int id;
		sscanf(s, "%d", &id);
		results.push_back(id);
	}
	delete[] s;
	fclose(f);
	return results;
}

VI overlap(VI a, VI b)
{
	sort(a.begin(), a.end());
	sort(b.begin(), b.end());
	VI c;
	for (int i = 0, j = 0; i < SIZE(a) && j < SIZE(b); )
		if (a[i] == b[j])
		{
			c.push_back(a[i]);
			i++;
			j++;
		}
		else if (a[i] < b[j])
			i++;
		else
			j++;
	return c;
}

VI getunion(VI a, VI b)
{
	sort(a.begin(), a.end());
	sort(b.begin(), b.end());
	VI c;
	int i, j;
	for (i = 0, j = 0; i < SIZE(a) && j < SIZE(b); )
		if (a[i] == b[j])
		{
			c.push_back(a[i]);
			i++;
			j++;
		}
		else if (a[i] < b[j])
		{
			c.push_back(a[i]);
			i++;
		}
		else
		{
			c.push_back(b[j]);
			j++;
		}
	for (; i < SIZE(a); ++i)
		c.push_back(a[i]);
	for (; j < SIZE(b); ++j)
		c.push_back(b[j]);
	return c;
}

void save_community(string filename, VI s)
{
	FILE *f = fopen(filename.c_str(), "w");
	for (int i = 0; i < SIZE(s); ++i)
		fprintf(f, "%d %s\n", s[i], names[s[i]].c_str());
	fclose(f);
}

double score_precision(VI a, VI b)
{
	SI sa, sb;
	for (int i = 0; i < SIZE(a); ++i)
		sa.insert(a[i]);
	for (int i = 0; i < SIZE(b); ++i)
		sb.insert(b[i]);
	int c1 = 0, c2 = 0;
	for (int i = 0; i < SIZE(b); ++i)
	{
		int key = b[i];
		for (int j = 0; j < degree[key]; ++j)
		{
			int other = g[key][j];
			if (sb.find(other) == sb.end())
				continue;
			++c1;
			if (sa.find(key) != sa.end() && sa.find(other) != sa.end())
				++c2;
		}
	}
	return (double)c2 / c1;
}

double score_recall(VI a, VI b)
{
	SI sa, sb;
	for (int i = 0; i < SIZE(a); ++i)
		sa.insert(a[i]);
	for (int i = 0; i < SIZE(b); ++i)
		sb.insert(b[i]);
	int c1 = 0, c2 = 0;
	for (int i = 0; i < SIZE(a); ++i)
	{
		int key = a[i];
		for (int j = 0; j < degree[key]; ++j)
		{
			int other = g[key][j];
			if (sa.find(other) == sa.end())
				continue;
			++c1;
			if (sb.find(key) != sb.end() && sb.find(other) != sb.end())
				++c2;
		}
	}
	return (double)c2 / c1;
}

double score_F(VI a, VI b)
{
	double p = score_precision(a, b);
	double r = score_recall(a, b);
	return 2 * p * r / (p + r);
}

double score_distance(VI a, VI b)
{
	VI c = overlap(a, b);
	return (double)(SIZE(c)) / (double)(SIZE(a) + SIZE(b) - SIZE(c));
}

double score(VI a, VI b, int t)
{
	if (t == 0) return score_precision(a, b);
	if (t == 1) return score_recall(a, b);
	if (t == 2) return score_F(a, b);
	if (t == 3) return score_distance(a, b);
	return 0;
}

int main()
{
	load_graph("..\\..\\Data\\GCRBC\\gc_data.txt");
	load_name("..\\..\\Data\\GCRBC\\gc_authors.txt");
	string datasets[5] = {"gc_AI.txt", "gc_DB.txt", "gc_DP.txt", "gc_GV.txt", "gc_NC.txt"};
	VI init_sets[5];
	for (int i = 0; i < 5; ++i)
		init_sets[i] = load_community(datasets[i]);
	double maxs[5][4];
	VI gs2[5], gs3[5];
	for (int i = 0; i < 5; ++i)
		for (int j = 0; j < 4; ++j)
			maxs[i][j] = 0;
	for (int step = 0; step < 1000; ++step)
	{
		srand(step);
		int key = step % 5;
		int csize = SIZE(init_sets[key]) * (rand() % 18000 + 2000) / 10000;
		VI src_set;
		int p = init_sets[key][rand() % SIZE(init_sets[key])];
		src_set.push_back(p);
		srand(step);
		VI results = annealing_improved(csize, src_set);
		double s0 = score_precision(init_sets[key], results);
		double s1 = score_recall(init_sets[key], results);
		double s2 = (2 * s0 * s1) / (s0 + s1);
		double s3 = score_distance(init_sets[key], results);
		if (s2 > maxs[key][2])
		{
			maxs[key][2] = s2;
			maxs[key][1] = s1;
			maxs[key][0] = s0;
			gs2[key] = results;
		}
		if (s3 > maxs[key][3])
		{
			maxs[key][3] = s3;
			gs3[key] = results;
		}
		if (step % 100 == 0)
		{
			printf("step = %d\n", step);
			for (int k = 0; k < 5; ++k)
			{
				for (int i = 0; i < 4; ++i)
					printf("%.6lf  ", maxs[k][i]);
				printf("\n");
			}
			printf("\n");
			FILE *f = fopen("tmp_results_weba.txt", "w");
			for (int k = 0; k < 5; ++k)
			{
				for (int i = 0; i < SIZE(gs2[k]); ++i)
					fprintf(f, "%d ", gs2[k][i]);
				fprintf(f, "\n");
				for (int i = 0; i < SIZE(gs3[k]); ++i)
					fprintf(f, "%d ", gs3[k][i]);
				fprintf(f, "\n\n");
			}
			fclose(f);
		}
	}	
	for (int k = 0; k < 5; ++k)
	{
		for (int i = 0; i < 4; ++i)
			printf("%.6lf  ", maxs[k][i]);
		printf("\n");
	}
	return 0;
}