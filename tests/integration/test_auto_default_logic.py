import pytest

from lib.entities import EmbeddingModelConfig, LLMModelConfig, LLMProvider
from lib.storage import Storage


@pytest.mark.asyncio
async def test_llm_auto_default_logic(storage: Storage):
    # Clear tables to remove auto-migrated models
    await storage._execute_with_connection(lambda db: db.execute("DELETE FROM llm_models"))

    # 1. Test auto-default on first creation
    model1 = LLMModelConfig(
        name="model1",
        provider=LLMProvider.OPENAI,
        model_name="gpt-4",
        is_default=False,  # Explicitly False
    )
    await storage.save_llm_model(model1)

    saved_model1 = await storage.get_llm_model("model1")
    assert saved_model1 is not None
    assert saved_model1.is_default is True, (
        "First model should be auto-set to default even if is_default=False"
    )

    # 2. Test adds second model (should NOT be default)
    model2 = LLMModelConfig(
        name="model2", provider=LLMProvider.ANTHROPIC, model_name="claude-3", is_default=False
    )
    await storage.save_llm_model(model2)

    saved_model2 = await storage.get_llm_model("model2")
    assert saved_model2.is_default is False

    # Verify model1 is still default
    saved_model1 = await storage.get_llm_model("model1")
    assert saved_model1.is_default is True

    # 3. Test auto-default on delete to one
    # Delete model1 (default), model2 should become default
    await storage.delete_llm_model("model1")

    saved_model2 = await storage.get_llm_model("model2")
    assert saved_model2.is_default is True, "Remaining single model should become default"

    # 4. Test default reassignment when multiple models exist
    # Setup: Create model3, ensure model2 is default.
    model3 = LLMModelConfig(
        name="model3", provider=LLMProvider.OLLAMA, model_name="llama2", is_default=False
    )
    await storage.save_llm_model(model3)

    # model2 is currently default. model3 is not.
    m2 = await storage.get_llm_model("model2")
    m3 = await storage.get_llm_model("model3")
    assert m2.is_default is True
    assert m3.is_default is False

    # Delete the current default (model2)
    # We expect model3 to become default (since it's the only other one, or alphabetical)
    await storage.delete_llm_model("model2")

    saved_model3 = await storage.get_llm_model("model3")
    assert saved_model3.is_default is True, (
        "Deleting default model should reassign default to available model"
    )


@pytest.mark.asyncio
async def test_embedding_auto_default_logic(storage: Storage):
    # Clear tables to remove auto-migrated models
    await storage._execute_with_connection(lambda db: db.execute("DELETE FROM embedding_models"))

    # 1. Test auto-default on first creation
    model1 = EmbeddingModelConfig(
        name="emb1",
        provider=LLMProvider.OPENAI,
        model_name="text-embedding-3-small",
        is_default=False,
    )
    await storage.save_embedding_model(model1)

    saved_model1 = await storage.get_embedding_model("emb1")
    assert saved_model1 is not None
    assert saved_model1.is_default is True, "First embedding model should be auto-set to default"

    # 2. Add second model
    model2 = EmbeddingModelConfig(
        name="emb2", provider=LLMProvider.GEMINI, model_name="embedding-001", is_default=False
    )
    await storage.save_embedding_model(model2)

    saved_model2 = await storage.get_embedding_model("emb2")
    assert saved_model2.is_default is False

    # 3. Test delete to one
    await storage.delete_embedding_model("emb1")

    saved_model2 = await storage.get_embedding_model("emb2")
    assert saved_model2.is_default is True, "Remaining single embedding model should become default"


@pytest.mark.asyncio
async def test_model_update_preserves_state(storage: Storage):
    # Clear tables
    await storage._execute_with_connection(lambda db: db.execute("DELETE FROM llm_models"))

    # 1. Create a default model
    model = LLMModelConfig(
        name="test-model",
        provider=LLMProvider.OPENAI,
        model_name="gpt-4",
        is_default=True,
    )
    await storage.save_llm_model(model)

    # 2. Update the model (changing provider and model_name)
    updated_model = LLMModelConfig(
        name="test-model",
        provider=LLMProvider.ANTHROPIC,
        model_name="claude-3",
        is_default=True,  # Frontend will now send this
        endpoint="https://api.anthropic.com",
    )
    await storage.save_llm_model(updated_model)

    # 3. Verify all fields updated and is_default is still True
    saved = await storage.get_llm_model("test-model")
    assert saved.provider == LLMProvider.ANTHROPIC
    assert saved.model_name == "claude-3"
    assert saved.endpoint == "https://api.anthropic.com"
    assert saved.is_default is True
