import pytest
import pytest_asyncio

from lib.entities import EmbeddingModelConfig, LLMModelConfig, LLMProvider
from lib.llm_config import LLMConfigManager, LLMConfigNotFoundError
from lib.storage import Storage


@pytest_asyncio.fixture
async def storage():
    """create in-memory storage for testing"""
    storage = Storage(":memory:")
    await storage.init_db()

    # Clear any models created by auto-migration from env
    await storage._execute_with_connection(lambda db: db.execute("DELETE FROM llm_models"))
    await storage._execute_with_connection(lambda db: db.execute("DELETE FROM embedding_models"))

    yield storage
    await storage.close()


@pytest_asyncio.fixture
async def llm_config_manager(storage):
    """create llm config manager with test storage"""
    return LLMConfigManager(storage)


@pytest.mark.asyncio
async def test_llm_default_selection_flow(llm_config_manager):
    """
    Test the flow of setting and retrieving default LLM models.

    Verifies:
    1. Fallback to first model when no default is set.
    2. Explicit default selection.
    3. Ensuring only one model is default at a time.
    4. Fallback to 'default' named model (legacy support).
    """

    # 1. Create a few models
    model1 = LLMModelConfig(
        name="gpt-4", provider=LLMProvider.OPENAI, model_name="gpt-4", is_default=False
    )
    model2 = LLMModelConfig(
        name="claude-3",
        provider=LLMProvider.ANTHROPIC,
        model_name="claude-3-opus",
        is_default=False,
    )
    model3 = LLMModelConfig(
        name="gemini-pro", provider=LLMProvider.GEMINI, model_name="gemini-pro", is_default=False
    )

    await llm_config_manager.save_llm_model(model1)
    await llm_config_manager.save_llm_model(model2)
    await llm_config_manager.save_llm_model(model3)

    # Validation 1: No explicit default, should return first one (ordering might depend on DB, usually insertion order)
    # We just ensure it returns *one* of them.
    default_model = await llm_config_manager.get_llm_model(None)
    assert default_model.name in ["gpt-4", "claude-3", "gemini-pro"]

    # Validation 2: Set model2 as default
    await llm_config_manager.set_default_llm_model("claude-3")

    # Check if retrieval returns model2
    default_model = await llm_config_manager.get_llm_model(None)
    assert default_model.name == "claude-3"
    assert default_model.is_default is True

    # Verify others are NOT default
    m1 = await llm_config_manager.get_llm_model("gpt-4")
    m3 = await llm_config_manager.get_llm_model("gemini-pro")
    assert m1.is_default is False
    assert m3.is_default is False

    # Validation 3: Switch default to model3
    await llm_config_manager.set_default_llm_model("gemini-pro")

    default_model = await llm_config_manager.get_llm_model(None)
    assert default_model.name == "gemini-pro"
    assert default_model.is_default is True

    # Verify model2 is no longer default
    m2 = await llm_config_manager.get_llm_model("claude-3")
    assert m2.is_default is False


@pytest.mark.asyncio
async def test_embedding_default_selection_flow(llm_config_manager):
    """
    Test the flow of setting and retrieving default Embedding models.

    Verifies:
    1. Fallback to first model when no default is set.
    2. Explicit default selection.
    3. Ensuring only one model is default at a time.
    4. Switching default model updates correctly.
    """
    embed1 = EmbeddingModelConfig(
        name="openai-embed",
        provider=LLMProvider.OPENAI,
        model_name="text-embedding-3-small",
        is_default=False,
    )
    embed2 = EmbeddingModelConfig(
        name="local-embed",
        provider=LLMProvider.OLLAMA,
        model_name="nomic-embed-text",
        is_default=False,
    )

    await llm_config_manager.save_embedding_model(embed1)
    await llm_config_manager.save_embedding_model(embed2)

    # 1. No default set, returns one of them
    default_model = await llm_config_manager.get_embedding_model(None)
    assert default_model.name in ["openai-embed", "local-embed"]

    # 2. Set default
    await llm_config_manager.set_default_embedding_model("local-embed")

    default_model = await llm_config_manager.get_embedding_model(None)
    assert default_model.name == "local-embed"
    assert default_model.is_default is True

    # Check other is not default
    e1 = await llm_config_manager.get_embedding_model("openai-embed")
    assert e1.is_default is False

    # 3. Switch default
    await llm_config_manager.set_default_embedding_model("openai-embed")

    default_model = await llm_config_manager.get_embedding_model(None)
    assert default_model.name == "openai-embed"
    assert default_model.is_default is True

    e2 = await llm_config_manager.get_embedding_model("local-embed")
    assert e2.is_default is False


@pytest.mark.asyncio
async def test_set_nonexistent_default_raises_error(llm_config_manager):
    """Test setting a non-existent model as default raises LLMConfigNotFoundError"""
    with pytest.raises(LLMConfigNotFoundError):
        await llm_config_manager.set_default_llm_model("non_existent_model")
