from sentence_transformers import SentenceTransformer, util
from src.db_management.manage_transactions import DBTransaction


class SemanticMatching:
    def __init__(self, config,  device='cpu', model_name='all-MiniLM-L6-v2'):
        self.config = config
        self.mg_trans = DBTransaction(config)
        self.model = SentenceTransformer(model_name)
        # self.ww_mission = """Wonders & Worries provides free, professional support for children and teenagers
        # ages 2-18 through a parent's serious illness or injury. The organization offers child life services,
        # illness education, and coping support to help children reach their full potential despite family health
        # challenges. Wonders & Worries aims to reduce anxiety, improve communication skills, and enhance school
        # performance for children affected by parental illness or injury. The charity's services include individual
        # and group support, delivered by Certified Child Life Specialists using a clinically validated curriculum.
        #  Wonders & Worries focuses on supporting families impacted by all types of physical illnesses and injuries,
        #  not limited to cancer, and offers services in both English and Spanish"""
        self.ww_mission = """parental illness coping support child life services general operation"""
        self.ww_encoded = self.model.encode(self.ww_mission)
        self.filer_grants = {}
        self.semantic_query = """
        SELECT EIN as ein, recipient as foundation, purpose as grant_purpose
        FROM grantsbyfiler
        WHERE purpose IS NOT NULL;
        """
        try:
            result = self.mg_trans.execute_independent(self.semantic_query)
            for row in result:
                ein = row[0]
                self.filer_grants[ein] = {
                    'foundation': row[1],
                    'grant_purpose': row[2],
                }
        except Exception as e:
            print(f"Semantic query failure: {e}")

    def compute_similarity(self, target_encoding, candidates):
        # target_embedding = self.model.encode(target_text, convert_to_tensor=True)
        candidate_embeddings = self.model.encode(candidates, convert_to_tensor=True)
        similarities = util.cos_sim(target_encoding, candidate_embeddings)
        return similarities

    def execute_semantic_analysis(self):
        insert_query = """
        INSERT INTO grant_semantic_score (EIN, foundation_name, purpose, similarity_score)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT DO NOTHING;
        """
        progress = 0
        total = 0
        for ein, grant_data in self.filer_grants.items():
            try:
                foundation = grant_data['foundation']
                purpose = grant_data['grant_purpose']
                if purpose and foundation:
                    comparator = " ".join((foundation, purpose))
                    score = self.compute_similarity(self.ww_encoded, [comparator])[0][0].item()
                    progress += 1
                    total += 1
                    if progress > 1000:
                        progress = 0
                        print(f"{total} scored")
                    if score > 0.2:
                        params = (ein, foundation, purpose, score)
                        self.mg_trans.execute_independent(insert_query, params=params)
            except Exception as e:
                print(f"Semantic analysis failure for EIN {ein}: {e}")

    def determine_similarity(self, ein):
        """Get similarity score for a foundation."""
        query = """
            SELECT similarity_score FROM grant_semantic_score 
            WHERE ein = %s;
            """
        try:
            result = self.mg_trans.execute_independent(query, params=(ein,))
            if result:
                score = result[0]
                return score
            else:
                return None
        except Exception as e:
            print(f"No similarity score found for foundation: {ein}")
            return None


