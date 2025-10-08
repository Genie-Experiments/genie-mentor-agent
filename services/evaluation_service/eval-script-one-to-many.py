import json
import os
from typing import List, Dict, Any
import pandas as pd
from datetime import datetime

# LlamaIndex imports
from llama_index.core import VectorStoreIndex, Document, Settings
from llama_index.core.retrievers import VectorIndexRetriever
from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.core.evaluation import (
    CorrectnessEvaluator,
    FaithfulnessEvaluator,
    RelevancyEvaluator,
    SemanticSimilarityEvaluator
)
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.groq import Groq


class RAGEvaluator:
    def __init__(self, embedding_model_name: str = "", groq_model_name: str = "", groq_api_key: str = ""):
        """
        Initialize the RAG evaluator

        Args:
            embedding_model_name: HuggingFace embedding model name (e.g., 'BAAI/bge-small-en-v1.5')
            groq_model_name: Groq model name (e.g., 'llama3-8b-8192')
            groq_api_key: Groq API key
        """
        self.embedding_model_name = embedding_model_name
        self.groq_model_name = groq_model_name
        self.groq_api_key = groq_api_key

        # Initialize components
        self._setup_models()
        self._setup_evaluators()

    def _setup_models(self):
        """Setup embedding model and LLM"""
        # Setup HuggingFace embedding model
        if self.embedding_model_name:
            self.embed_model = HuggingFaceEmbedding(
                model_name=self.embedding_model_name)
        else:
            raise ValueError("Please provide an embedding model name")

        # Setup Groq LLM
        if self.groq_model_name and self.groq_api_key:
            self.llm = Groq(model=self.groq_model_name,
                            api_key=self.groq_api_key)
        else:
            raise ValueError("Please provide Groq model name and API key")

        # Configure global settings
        Settings.embed_model = self.embed_model
        Settings.llm = self.llm

    def _setup_evaluators(self):
        """Setup evaluation metrics"""
        self.evaluators = {
            'correctness': CorrectnessEvaluator(llm=self.llm),
            'faithfulness': FaithfulnessEvaluator(llm=self.llm),
            'relevancy': RelevancyEvaluator(llm=self.llm),
            'semantic_similarity': SemanticSimilarityEvaluator(embed_model=self.embed_model)
        }

    def load_eval_dataset(self, eval_data_path: str) -> List[Dict[str, Any]]:
        """Load evaluation dataset"""
        with open(eval_data_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def load_actual_data(self, actual_data_path: str) -> List[Dict[str, Any]]:
        """Load actual data for creating the knowledge base"""
        with open(actual_data_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def create_index(self, actual_data: List[Dict[str, Any]]) -> VectorStoreIndex:
        """Create vector store index from actual data"""
        print("Creating vector store index...")

        # Convert data to LlamaIndex Document objects
        documents = []
        for item in actual_data:
            doc = Document(
                text=item['text'],
                metadata=item['metadata']
            )
            documents.append(doc)

        # Create index
        index = VectorStoreIndex.from_documents(documents)
        print(f"Created index with {len(documents)} documents")

        return index

    def create_retriever(self, index: VectorStoreIndex, top_k: int = 5) -> VectorIndexRetriever:
        """Create retriever from index"""
        retriever = VectorIndexRetriever(
            index=index,
            similarity_top_k=top_k
        )
        return retriever

    def create_query_engine(self, retriever: VectorIndexRetriever) -> RetrieverQueryEngine:
        """Create query engine from retriever"""
        query_engine = RetrieverQueryEngine(retriever=retriever)
        return query_engine

    def evaluate_single_question(self, question: str, expected_answer: str,
                                 context: str, query_engine: RetrieverQueryEngine) -> Dict[str, float]:
        """Evaluate a single question across all metrics"""
        print(f"Evaluating question: {question[:50]}...")

        # Generate response
        response = query_engine.query(question)

        results = {
            "generated_answer": str(response)
        }

        # Run each evaluator
        for metric_name, evaluator in self.evaluators.items():
            try:
                if metric_name == 'correctness':
                    eval_result = evaluator.evaluate(
                        query=question,
                        response=str(response),
                        reference=expected_answer
                    )
                elif metric_name == 'faithfulness':
                    eval_result = evaluator.evaluate(
                        query=question,
                        response=str(response),
                        contexts=[context]
                    )
                elif metric_name == 'relevancy':
                    eval_result = evaluator.evaluate(
                        query=question,
                        response=str(response),
                        contexts=[context]
                    )
                elif metric_name == 'semantic_similarity':
                    eval_result = evaluator.evaluate(
                        query=question,
                        response=str(response),
                        reference=expected_answer
                    )

                results[metric_name] = eval_result.score if hasattr(
                    eval_result, 'score') else eval_result

            except Exception as e:
                print(f"Error evaluating {metric_name}: {str(e)}")
                results[metric_name] = 0.0

        return results

    def run_evaluation(self, eval_data_path: str, actual_data_path: str,
                       top_k: int = 5, output_file: str = None) -> pd.DataFrame:
        """Run full evaluation pipeline"""
        print("Starting RAG evaluation...")

        # Load data
        eval_dataset = self.load_eval_dataset(eval_data_path)
        actual_data = self.load_actual_data(actual_data_path)

        # Create index and retriever
        index = self.create_index(actual_data)
        retriever = self.create_retriever(index, top_k=top_k)
        query_engine = self.create_query_engine(retriever)

        # Run evaluation
        all_results = []

        for eval_item in eval_dataset:
            context = eval_item['context']
            metadata = eval_item['metadata']

            for question_data in eval_item['questions']:
                question = question_data['question']
                expected_answer = question_data['answer']

                if not question.strip():  # Skip empty questions
                    continue

                # Evaluate this question
                results = self.evaluate_single_question(
                    question=question,
                    expected_answer=expected_answer,
                    context=context,
                    query_engine=query_engine
                )

                # Store results
                result_row = {
                    'query': question,
                    'expected_answer': expected_answer,
                    'context': context,
                    'page_number': metadata.get('page_number', ''),
                    'header': metadata.get('header', ''),
                    'chunk_index': metadata.get('chunk_index', ''),
                    'file_path': metadata.get('file_path', ''),
                    'token_count': metadata.get('token_count', ''),
                    **results
                }

                all_results.append(result_row)

        # Create DataFrame
        results_df = pd.DataFrame(all_results)

        # Calculate summary statistics
        self._print_summary(results_df)

        # Save results if output file specified
        if output_file:
            results_df.to_csv(output_file, index=False)
            print(f"Results saved to {output_file}")

        return results_df

    def _print_summary(self, results_df: pd.DataFrame):
        """Print evaluation summary"""
        print("\n" + "="*60)
        print("EVALUATION SUMMARY")
        print("="*60)

        metrics = ['correctness', 'faithfulness',
                   'relevancy', 'semantic_similarity']

        for metric in metrics:
            if metric in results_df.columns:
                avg_score = results_df[metric].mean()
                print(f"{metric.capitalize()}: {avg_score:.4f}")

        print(f"\nTotal questions evaluated: {len(results_df)}")
        print("="*60)


def main():
    """Main function to run the evaluation"""

    # Configuration - UPDATE THESE VALUES
    # e.g., "BAAI/bge-small-en-v1.5", "sentence-transformers/all-MiniLM-L6-v2"
    EMBEDDING_MODEL = "BAAI/bge-small-en-v1.5"
    # e.g., "llama3-8b-8192", "mixtral-8x7b-32768"
    GROQ_MODEL = "meta-llama/llama-4-scout-17b-16e-instruct"
    # Your Groq API key
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")

    # File paths - UPDATE THESE PATHS
    # Path to your evaluation dataset
    EVAL_DATA_PATH = "./eval_data/Advanced RAG.json"
    ACTUAL_DATA_PATH = "./data/Advanced RAG.pdf.json"     # Path to your actual data
    OUTPUT_FILE = f"evaluation_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

    # Validation
    if not EMBEDDING_MODEL:
        print("ERROR: Please set EMBEDDING_MODEL")
        print(
            "Example: 'BAAI/bge-small-en-v1.5' or 'sentence-transformers/all-MiniLM-L6-v2'")
        return

    if not GROQ_MODEL:
        print("ERROR: Please set GROQ_MODEL")
        print("Example: 'llama3-8b-8192' or 'mixtral-8x7b-32768'")
        return

    if not GROQ_API_KEY:
        print("ERROR: Please set GROQ_API_KEY")
        return

    if not os.path.exists(EVAL_DATA_PATH):
        print(f"ERROR: Evaluation dataset not found at {EVAL_DATA_PATH}")
        return

    if not os.path.exists(ACTUAL_DATA_PATH):
        print(f"ERROR: Actual data not found at {ACTUAL_DATA_PATH}")
        return

    try:
        # Initialize evaluator
        evaluator = RAGEvaluator(
            embedding_model_name=EMBEDDING_MODEL,
            groq_model_name=GROQ_MODEL,
            groq_api_key=GROQ_API_KEY
        )

        # Run evaluation
        results_df = evaluator.run_evaluation(
            eval_data_path=EVAL_DATA_PATH,
            actual_data_path=ACTUAL_DATA_PATH,
            top_k=5,
            output_file=OUTPUT_FILE
        )

        print(f"\nEvaluation completed successfully!")
        print(f"Results saved to: {OUTPUT_FILE}")

    except Exception as e:
        print(f"Error during evaluation: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
