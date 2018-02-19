typedef struct bgen_string {
  int len;
  char *str;
} bgen_string;

struct BGenVar {
  bgen_string id;
  bgen_string rsid;
  bgen_string chrom;
  int position;
  int nalleles;
  bgen_string *allele_ids;
};

struct BGenFile *open_bgen(const char *filepath);

void close_bgen(struct BGenFile *bgen);

int get_nsamples(struct BGenFile *bgen);

int get_nvariants(struct BGenFile *bgen);

bgen_string *read_samples(struct BGenFile *bgen);

void free_samples(const struct BGenFile *bgen, bgen_string *samples);

struct BGenVar *read_variants(struct BGenFile *bgen, struct BGenVI **index);

void free_variants(const struct BGenFile *bgen, struct BGenVar *variants);

void free_index(struct BGenVI *index);

struct BGenVG *open_variant_genotype(struct BGenVI *index, size_t variant_idx);

void read_variant_genotype(struct BGenVI *index, struct BGenVG *vg,
                           double *probabilities);

int get_nalleles(struct BGenVG *vg);
int get_ploidy(struct BGenVG *vg);
int get_ncombs(struct BGenVG *vg);

void close_variant_genotype(struct BGenVI *index, struct BGenVG *vg);

void free(void *);

bgen_string string_duplicate(const bgen_string s);

int sample_ids_presence(struct BGenFile *bgen);
