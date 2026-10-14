import { useEffect, useState } from "react";
import {
  getNotebooks,
  createNotebook,
  updateNotebook,
  deleteNotebook,
  getDocuments,
  uploadDocument,
  addWebsite,
  askQuestion,
  getChatMessages,
  generateSummary,
  generateStudyGuide,
  generateQuiz,
} from "./services/api";
import "./App.css";

function App() {
  const [notebooks, setNotebooks] = useState([]);
  const [selectedNotebookId, setSelectedNotebookId] = useState(null);

  const [studyMaterial, setStudyMaterial] = useState(null);
  const [studyToolLoading, setStudyToolLoading] = useState(false);
  const [studyToolError, setStudyToolError] = useState("");

  const [loadingNotebooks, setLoadingNotebooks] = useState(true);
  const [error, setError] = useState("");

  const [showCreateForm, setShowCreateForm] = useState(false);
  const [newNotebookTitle, setNewNotebookTitle] = useState("");
  const [newNotebookDescription, setNewNotebookDescription] = useState("");
  const [creatingNotebook, setCreatingNotebook] = useState(false);
  const [createError, setCreateError] = useState("");

  const [editingNotebookId, setEditingNotebookId] = useState(null);
  const [editNotebookTitle, setEditNotebookTitle] = useState("");
  const [editNotebookDescription, setEditNotebookDescription] = useState("");
  const [savingNotebook, setSavingNotebook] = useState(false);
  const [notebookActionError, setNotebookActionError] = useState("");
  const [deletingNotebookId, setDeletingNotebookId] = useState(null);

  const [documents, setDocuments] = useState([]);
  const [loadingDocuments, setLoadingDocuments] = useState(false);
  const [documentsError, setDocumentsError] = useState("");

  const [messages, setMessages] = useState([]);
  const [loadingMessages, setLoadingMessages] = useState(false);
  const [chatQuestion, setChatQuestion] = useState("");
  const [sendingMessage, setSendingMessage] = useState(false);
  const [chatError, setChatError] = useState("");

  const [uploadingDocument, setUploadingDocument] = useState(false);
  const [sourceActionError, setSourceActionError] = useState("");

  const [showWebsiteForm, setShowWebsiteForm] = useState(false);
  const [websiteUrl, setWebsiteUrl] = useState("");
  const [addingWebsite, setAddingWebsite] = useState(false);
  const [websiteError, setWebsiteError] = useState("");

  useEffect(() => {
    let cancelled = false;

    const loadNotebooks = async () => {
      try {
        setLoadingNotebooks(true);
        setError("");

        const data = await getNotebooks();

        if (cancelled) return;

        const notebookList = Array.isArray(data) ? data : [];

        setNotebooks(notebookList);

        setSelectedNotebookId((currentId) => {
          if (
            currentId !== null &&
            notebookList.some((notebook) => notebook.id === currentId)
          ) {
            return currentId;
          }

          return notebookList.length > 0 ? notebookList[0].id : null;
        });
      } catch (err) {
        if (!cancelled) {
          console.error("Failed to load notebooks:", err);

          setError(
            err.response?.data?.detail ||
              "Unable to load notebooks. Please check your backend connection."
          );
        }
      } finally {
        if (!cancelled) {
          setLoadingNotebooks(false);
        }
      }
    };

    loadNotebooks();

    return () => {
      cancelled = true;
    };
  }, []);

  useEffect(() => {
    let cancelled = false;

    const loadDocuments = async () => {
      if (selectedNotebookId === null) {
        setDocuments([]);
        setDocumentsError("");
        setLoadingDocuments(false);
        return;
      }

      try {
        setLoadingDocuments(true);
        setDocumentsError("");

        const data = await getDocuments(selectedNotebookId);

        if (!cancelled) {
          setDocuments(Array.isArray(data) ? data : []);
        }
      } catch (err) {
        if (!cancelled) {
          console.error("Failed to load documents:", err);

          setDocumentsError(
            err.response?.data?.detail || "Unable to load sources."
          );

          setDocuments([]);
        }
      } finally {
        if (!cancelled) {
          setLoadingDocuments(false);
        }
      }
    };

    loadDocuments();

    return () => {
      cancelled = true;
    };
  }, [selectedNotebookId]);

  useEffect(() => {
    let cancelled = false;

    const loadMessages = async () => {
      if (selectedNotebookId === null) {
        setMessages([]);
        setChatError("");
        setLoadingMessages(false);
        return;
      }

      try {
        setLoadingMessages(true);
        setChatError("");

        const data = await getChatMessages(selectedNotebookId);

        if (!cancelled) {
          setMessages(Array.isArray(data) ? data : []);
        }
      } catch (err) {
        if (!cancelled) {
          console.error("Failed to load chat history:", err);

          setChatError(
            err.response?.data?.detail ||
              "Unable to load chat history. You can still try asking a question."
          );
        }
      } finally {
        if (!cancelled) {
          setLoadingMessages(false);
        }
      }
    };

    loadMessages();

    return () => {
      cancelled = true;
    };
  }, [selectedNotebookId]);

  const handleCreateNotebook = async (event) => {
    event.preventDefault();

    const title = newNotebookTitle.trim();
    const description = newNotebookDescription.trim();

    if (!title || creatingNotebook) return;

    try {
      setCreatingNotebook(true);
      setCreateError("");

      const notebook = await createNotebook({
        title,
        description,
      });

      setNotebooks((previousNotebooks) => [
        notebook,
        ...previousNotebooks,
      ]);

      setSelectedNotebookId(notebook.id);

      setNewNotebookTitle("");
      setNewNotebookDescription("");
      setShowCreateForm(false);
    } catch (err) {
      console.error("Failed to create notebook:", err);

      setCreateError(
        err.response?.data?.detail || "Unable to create notebook."
      );
    } finally {
      setCreatingNotebook(false);
    }
  };

  const handleStartEditing = (event, notebook) => {
    event.stopPropagation();

    setNotebookActionError("");

    setEditingNotebookId(notebook.id);
    setEditNotebookTitle(notebook.title || "");
    setEditNotebookDescription(notebook.description || "");
  };

  const handleCancelEditing = () => {
    setEditingNotebookId(null);
    setEditNotebookTitle("");
    setEditNotebookDescription("");
    setNotebookActionError("");
  };

  const handleSaveNotebook = async (event, notebookId) => {
    event.preventDefault();

    const title = editNotebookTitle.trim();
    const description = editNotebookDescription.trim();

    if (!title || savingNotebook) return;

    try {
      setSavingNotebook(true);
      setNotebookActionError("");

      const updatedNotebook = await updateNotebook(notebookId, {
        title,
        description,
      });

      setNotebooks((previousNotebooks) =>
        previousNotebooks.map((notebook) =>
          notebook.id === notebookId
            ? {
                ...notebook,
                ...updatedNotebook,
                title,
                description,
              }
            : notebook
        )
      );

      handleCancelEditing();
    } catch (err) {
      console.error("Failed to update notebook:", err);

      setNotebookActionError(
        err.response?.data?.detail || "Unable to update notebook."
      );
    } finally {
      setSavingNotebook(false);
    }
  };

  const handleDeleteNotebook = async (event, notebook) => {
    event.stopPropagation();

    const confirmed = window.confirm(
      `Are you sure you want to delete "${notebook.title}"?\n\nThis action cannot be undone.`
    );

    if (!confirmed || deletingNotebookId !== null) return;

    try {
      setDeletingNotebookId(notebook.id);
      setNotebookActionError("");

      await deleteNotebook(notebook.id);

      const remainingNotebooks = notebooks.filter(
        (item) => item.id !== notebook.id
      );

      setNotebooks(remainingNotebooks);

      if (selectedNotebookId === notebook.id) {
        setSelectedNotebookId(
          remainingNotebooks.length > 0 ? remainingNotebooks[0].id : null
        );
      }

      if (editingNotebookId === notebook.id) {
        handleCancelEditing();
      }

      setStudyMaterial(null);
      setStudyToolError("");
    } catch (err) {
      console.error("Failed to delete notebook:", err);

      setNotebookActionError(
        err.response?.data?.detail || "Unable to delete notebook."
      );
    } finally {
      setDeletingNotebookId(null);
    }
  };

  const handleUploadDocument = async (event) => {
    const file = event.target.files?.[0];

    event.target.value = "";

    if (!file || selectedNotebookId === null || uploadingDocument) {
      return;
    }

    try {
      setUploadingDocument(true);
      setSourceActionError("");
      setDocumentsError("");

      await uploadDocument(selectedNotebookId, file);

      const updatedDocuments = await getDocuments(selectedNotebookId);

      setDocuments(
        Array.isArray(updatedDocuments) ? updatedDocuments : []
      );
    } catch (err) {
      console.error("Failed to upload document:", err);

      setSourceActionError(
        err.response?.data?.detail || "Unable to upload this file."
      );
    } finally {
      setUploadingDocument(false);
    }
  };

  const handleAddWebsite = async (event) => {
    event.preventDefault();

    const url = websiteUrl.trim();

    if (!url || selectedNotebookId === null || addingWebsite) {
      return;
    }

    try {
      setAddingWebsite(true);
      setWebsiteError("");
      setSourceActionError("");
      setDocumentsError("");

      await addWebsite(selectedNotebookId, url);

      const updatedDocuments = await getDocuments(selectedNotebookId);

      setDocuments(
        Array.isArray(updatedDocuments) ? updatedDocuments : []
      );

      setWebsiteUrl("");
      setShowWebsiteForm(false);
    } catch (err) {
      console.error("Failed to add website:", err);

      setWebsiteError(
        err.response?.data?.detail || "Unable to add this website."
      );
    } finally {
      setAddingWebsite(false);
    }
  };

  const handleSendMessage = async (event) => {
    event.preventDefault();

    const question = chatQuestion.trim();

    if (
      !question ||
      selectedNotebookId === null ||
      sendingMessage
    ) {
      return;
    }

    const notebookId = selectedNotebookId;

    try {
      setSendingMessage(true);
      setChatError("");
      setChatQuestion("");

      setMessages((previousMessages) => [
        ...previousMessages,
        {
          id: `temp-${Date.now()}`,
          role: "user",
          content: question,
        },
      ]);

      await askQuestion(notebookId, question);

      const updatedMessages = await getChatMessages(notebookId);

      setMessages(Array.isArray(updatedMessages) ? updatedMessages : []);
    } catch (err) {
      console.error("Failed to send message:", err);

      const detail = err.response?.data?.detail;

      setChatError(
        typeof detail === "string"
          ? detail
          : "Unable to get an answer. Please try again."
      );

      setChatQuestion(question);

      try {
        const updatedMessages = await getChatMessages(notebookId);

        setMessages(
          Array.isArray(updatedMessages) ? updatedMessages : []
        );
      } catch (historyError) {
        console.error("Failed to reload chat history:", historyError);
      }
    } finally {
      setSendingMessage(false);
    }
  };

  const handleGenerateSummary = async () => {
    if (!selectedNotebook || studyToolLoading) return;

    setStudyToolLoading(true);
    setStudyToolError("");
    setStudyMaterial(null);

    try {
      const result = await generateSummary(selectedNotebook.id);

      setStudyMaterial({
        type: "Summary",
        content: result,
      });
    } catch (err) {
      setStudyToolError(
        err.response?.data?.detail || "Failed to generate summary."
      );
    } finally {
      setStudyToolLoading(false);
    }
  };

  const handleGenerateStudyGuide = async () => {
    if (!selectedNotebook || studyToolLoading) return;

    setStudyToolLoading(true);
    setStudyToolError("");
    setStudyMaterial(null);

    try {
      const result = await generateStudyGuide(selectedNotebook.id);

      setStudyMaterial({
        type: "Study Guide",
        content: result,
      });
    } catch (err) {
      setStudyToolError(
        err.response?.data?.detail || "Failed to generate study guide."
      );
    } finally {
      setStudyToolLoading(false);
    }
  };

  const handleGenerateQuiz = async () => {
    if (!selectedNotebook || studyToolLoading) return;

    setStudyToolLoading(true);
    setStudyToolError("");
    setStudyMaterial(null);

    try {
      const result = await generateQuiz(selectedNotebook.id, 5);

      setStudyMaterial({
        type: "Quiz",
        content: result,
      });
    } catch (err) {
      setStudyToolError(
        err.response?.data?.detail || "Failed to generate quiz."
      );
    } finally {
      setStudyToolLoading(false);
    }
  };

  const handleChatKeyDown = (event) => {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      event.currentTarget.form?.requestSubmit();
    }
  };

  const selectedNotebook = notebooks.find(
    (notebook) => notebook.id === selectedNotebookId
  );

  const getMessageRole = (message) => {
    const role = (
      message.role ||
      message.sender ||
      message.message_type ||
      ""
    ).toLowerCase();

    return ["user", "human"].includes(role) ? "user" : "assistant";
  };

  const getMessageContent = (message) => {
    return (
      message.content ??
      message.message ??
      message.answer ??
      message.question ??
      ""
    );
  };

  return (
    <div className="app-container">
      {/* Header */}
      <header className="app-header">
        <div className="header-brand">
          <div className="brand-icon">N</div>

          <div>
            <h1>AI Notebook</h1>
            <p>Your personal AI research assistant</p>
          </div>
        </div>

        <div className="header-status">
          <span className="status-dot" />
          AI-Powered Research
        </div>
      </header>

      {/* Main workspace */}
      <main className="workspace">
        {/* Notebook sidebar */}
        <aside className="notebook-sidebar">
          <div className="sidebar-heading">
            <div>
              <h2>My Notebooks</h2>
              <p>Organize your research</p>
            </div>

            <button
              type="button"
              className="primary-button"
              onClick={() => {
                setShowCreateForm((previous) => !previous);
                setCreateError("");
              }}
            >
              {showCreateForm ? "Cancel" : "+ New"}
            </button>
          </div>

          {showCreateForm && (
            <form
              className="create-notebook-form"
              onSubmit={handleCreateNotebook}
            >
              <label htmlFor="notebook-title">Notebook title</label>

              <input
                id="notebook-title"
                type="text"
                value={newNotebookTitle}
                onChange={(event) =>
                  setNewNotebookTitle(event.target.value)
                }
                placeholder="e.g. Machine Learning Research"
                required
                maxLength={200}
              />

              <label htmlFor="notebook-description">Description</label>

              <textarea
                id="notebook-description"
                value={newNotebookDescription}
                onChange={(event) =>
                  setNewNotebookDescription(event.target.value)
                }
                placeholder="What is this notebook about?"
                rows={3}
              />

              {createError && (
                <p className="error-message">{createError}</p>
              )}

              <button
                type="submit"
                className="primary-button full-width"
                disabled={
                  creatingNotebook || !newNotebookTitle.trim()
                }
              >
                {creatingNotebook ? "Creating..." : "Create Notebook"}
              </button>
            </form>
          )}

          {notebookActionError && (
            <p className="error-message" role="alert">
              {notebookActionError}
            </p>
          )}

          {loadingNotebooks ? (
            <p className="empty-state">Loading notebooks...</p>
          ) : error ? (
            <div className="error-message">
              <p>{error}</p>

              <button
                type="button"
                className="secondary-button"
                onClick={() => window.location.reload()}
              >
                Retry
              </button>
            </div>
          ) : notebooks.length === 0 ? (
            <div className="empty-state">
              <p>No notebooks yet.</p>
              <p>Create one to get started.</p>
            </div>
          ) : (
            <div className="notebook-list">
              {notebooks.map((notebook) => (
                <div
                  key={notebook.id}
                  className={`notebook-card ${
                    selectedNotebookId === notebook.id ? "active" : ""
                  }`}
                >
                  {editingNotebookId === notebook.id ? (
                    <form
                      className="edit-notebook-form"
                      onSubmit={(event) =>
                        handleSaveNotebook(event, notebook.id)
                      }
                    >
                      <label htmlFor={`edit-title-${notebook.id}`}>
                        Title
                      </label>

                      <input
                        id={`edit-title-${notebook.id}`}
                        type="text"
                        value={editNotebookTitle}
                        onChange={(event) =>
                          setEditNotebookTitle(event.target.value)
                        }
                        maxLength={200}
                        required
                      />

                      <label htmlFor={`edit-description-${notebook.id}`}>
                        Description
                      </label>

                      <textarea
                        id={`edit-description-${notebook.id}`}
                        value={editNotebookDescription}
                        onChange={(event) =>
                          setEditNotebookDescription(event.target.value)
                        }
                        rows={3}
                      />

                      <div className="notebook-edit-actions">
                        <button
                          type="submit"
                          className="primary-button"
                          disabled={
                            savingNotebook || !editNotebookTitle.trim()
                          }
                        >
                          {savingNotebook ? "Saving..." : "Save"}
                        </button>

                        <button
                          type="button"
                          className="secondary-button"
                          onClick={handleCancelEditing}
                          disabled={savingNotebook}
                        >
                          Cancel
                        </button>
                      </div>
                    </form>
                  ) : (
                    <>
                      <button
                        type="button"
                        className={`notebook-item ${
                          selectedNotebookId === notebook.id ? "active" : ""
                        }`}
                        onClick={() => {
                          setSelectedNotebookId(notebook.id);
                          setNotebookActionError("");
                        }}
                      >
                        <span className="notebook-icon">📓</span>

                        <span className="notebook-item-content">
                          <strong>{notebook.title}</strong>

                          <span>
                            {notebook.description ||
                              "No description provided"}
                          </span>
                        </span>
                      </button>

                      <div className="notebook-actions">
                        <button
                          type="button"
                          className="notebook-action-button"
                          onClick={(event) =>
                            handleStartEditing(event, notebook)
                          }
                          aria-label={`Edit ${notebook.title}`}
                          title="Edit notebook"
                          disabled={deletingNotebookId !== null}
                        >
                          ✏️
                        </button>

                        <button
                          type="button"
                          className="notebook-action-button delete-action"
                          onClick={(event) =>
                            handleDeleteNotebook(event, notebook)
                          }
                          aria-label={`Delete ${notebook.title}`}
                          title="Delete notebook"
                          disabled={deletingNotebookId !== null}
                        >
                          {deletingNotebookId === notebook.id
                            ? "…"
                            : "🗑️"}
                        </button>
                      </div>
                    </>
                  )}
                </div>
              ))}
            </div>
          )}
        </aside>

        {/* Main content */}
        <section className="main-content">
          {!selectedNotebook ? (
            <div className="welcome-panel">
              <h2>Welcome to AI Notebook</h2>

              <p>
                Create or select a notebook to begin organizing your
                sources and asking questions.
              </p>

              <button
                type="button"
                className="primary-button"
                onClick={() => setShowCreateForm(true)}
              >
                Create Your First Notebook
              </button>
            </div>
          ) : (
            <>
              {/* Notebook heading */}
              <div className="notebook-header">
                <div>
                  <h2>{selectedNotebook.title}</h2>

                  <p>
                    {selectedNotebook.description ||
                      "Add sources and start exploring your research."}
                  </p>
                </div>
              </div>

              {/* Sources panel */}
              <section className="sources-panel">
                <div className="section-heading">
                  <div>
                    <h3>Sources</h3>

                    <p>
                      Add documents and websites for your AI to reference.
                    </p>
                  </div>

                  <span className="source-count">
                    {documents.length}{" "}
                    {documents.length === 1 ? "source" : "sources"}
                  </span>
                </div>

                <div className="source-actions">
                  <label
                    className={`secondary-button ${
                      uploadingDocument ? "disabled" : ""
                    }`}
                  >
                    {uploadingDocument ? "Uploading..." : "+ Upload File"}

                    <input
                      type="file"
                      accept=".pdf,.txt,.md,.docx,.pptx"
                      onChange={handleUploadDocument}
                      disabled={uploadingDocument}
                      hidden
                    />
                  </label>

                  <button
                    type="button"
                    className="secondary-button"
                    onClick={() => {
                      setShowWebsiteForm((previous) => !previous);
                      setWebsiteError("");
                      setSourceActionError("");
                    }}
                  >
                    {showWebsiteForm ? "Cancel" : "+ Add Website"}
                  </button>
                </div>

                {showWebsiteForm && (
                  <form
                    className="website-form"
                    onSubmit={handleAddWebsite}
                  >
                    <label htmlFor="website-url">Website URL</label>

                    <div className="website-input-row">
                      <input
                        id="website-url"
                        type="url"
                        value={websiteUrl}
                        onChange={(event) =>
                          setWebsiteUrl(event.target.value)
                        }
                        placeholder="https://example.com/article"
                        required
                      />

                      <button
                        type="submit"
                        className="primary-button"
                        disabled={addingWebsite || !websiteUrl.trim()}
                      >
                        {addingWebsite ? "Adding..." : "Add"}
                      </button>
                    </div>

                    {websiteError && (
                      <p className="error-message">{websiteError}</p>
                    )}
                  </form>
                )}

                {sourceActionError && (
                  <p className="error-message">{sourceActionError}</p>
                )}

                {documentsError && (
                  <p className="error-message">{documentsError}</p>
                )}

                {loadingDocuments ? (
                  <p className="empty-state">Loading sources...</p>
                ) : documents.length === 0 ? (
                  <div className="empty-state">
                    <p>No sources added yet.</p>

                    <p>
                      Upload a document or add a website to get started.
                    </p>
                  </div>
                ) : (
                  <div className="source-list">
                    {documents.map((document) => (
                      <div className="source-item" key={document.id}>
                        <span className="source-icon">
                          {document.source_type === "url" || document.url
                            ? "🌐"
                            : "📄"}
                        </span>

                        <div className="source-item-content">
                          <strong>
                            {document.title ||
                              document.filename ||
                              document.url ||
                              `Source ${document.id}`}
                          </strong>

                          <span>
                            {document.source_type ||
                              (document.url ? "Website" : "Document")}
                          </span>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </section>

              {/* Chat panel */}
              <section className="chat-panel">
                <div className="section-heading chat-heading">
                  <div>
                    <h3>Chat with your sources</h3>

                    <p>
                      Ask questions and get answers based on your notebook.
                    </p>
                  </div>
                </div>

                <div className="chat-messages">
                  {loadingMessages && messages.length === 0 ? (
                    <div className="chat-status">
                      Loading conversation...
                    </div>
                  ) : messages.length === 0 ? (
                    <div className="chat-empty-state">
                      <div className="chat-empty-icon">✦</div>

                      <h4>What would you like to learn?</h4>

                      <p>
                        Ask a question about the sources in this notebook.
                      </p>

                      {documents.length > 0 && (
                        <div className="suggestion-list">
                          <button
                            type="button"
                            onClick={() =>
                              setChatQuestion(
                                "Summarize the key points from my sources."
                              )
                            }
                          >
                            Summarize my sources
                          </button>

                          <button
                            type="button"
                            onClick={() =>
                              setChatQuestion(
                                "What are the most important concepts in my sources?"
                              )
                            }
                          >
                            Identify key concepts
                          </button>

                          <button
                            type="button"
                            onClick={() =>
                              setChatQuestion(
                                "What connections exist between my sources?"
                              )
                            }
                          >
                            Find connections
                          </button>
                        </div>
                      )}
                    </div>
                  ) : (
                    messages.map((message, index) => {
                      const role = getMessageRole(message);
                      const content = getMessageContent(message);

                      return (
                        <div
                          className={`chat-message ${
                            role === "user"
                              ? "user-message"
                              : "assistant-message"
                          }`}
                          key={message.id ?? `${role}-${index}`}
                        >
                          <div className="message-avatar">
                            {role === "user" ? "YOU" : "AI"}
                          </div>

                          <div className="message-content">
                            <strong>
                              {role === "user" ? "You" : "AI Assistant"}
                            </strong>

                            <p>
                              {typeof content === "string"
                                ? content
                                : JSON.stringify(content)}
                            </p>
                          </div>
                        </div>
                      );
                    })
                  )}

                  {sendingMessage && (
                    <div className="chat-message assistant-message">
                      <div className="message-avatar">AI</div>

                      <div className="message-content">
                        <strong>AI Assistant</strong>
                        <p>Thinking...</p>
                      </div>
                    </div>
                  )}
                </div>

                {chatError && (
                  <div className="chat-error" role="alert">
                    {chatError}
                  </div>
                )}

                <form
                  className="chat-input-area"
                  onSubmit={handleSendMessage}
                >
                  <textarea
                    value={chatQuestion}
                    onChange={(event) =>
                      setChatQuestion(event.target.value)
                    }
                    onKeyDown={handleChatKeyDown}
                    placeholder="Ask a question about your sources..."
                    rows={2}
                    disabled={sendingMessage}
                    aria-label="Ask a question"
                  />

                  <div className="chat-input-footer">
                    <span className="input-hint">
                      Enter to send · Shift + Enter for a new line
                    </span>

                    <button
                      type="submit"
                      className="send-button"
                      disabled={sendingMessage || !chatQuestion.trim()}
                    >
                      {sendingMessage ? "Sending..." : "Send ↑"}
                    </button>
                  </div>
                </form>
              </section>
            </>
          )}
        </section>
      </main>

      {/* Study material loading */}
      {studyToolLoading && (
        <div className="study-material-panel">
          <p>Generating your study material...</p>
        </div>
      )}

      {/* Study material error */}
      {studyToolError && (
        <div className="study-material-error">
          <p>{studyToolError}</p>
        </div>
      )}

      {/* Study material result */}
      {studyMaterial && (
        <section className="study-material-panel">
          <div className="study-material-header">
            <h2>{studyMaterial.type}</h2>

            <button
              type="button"
              onClick={() => setStudyMaterial(null)}
              aria-label="Close study material"
            >
              ✕
            </button>
          </div>

          <pre className="study-material-content">
            {typeof studyMaterial.content === "string"
              ? studyMaterial.content
              : JSON.stringify(studyMaterial.content, null, 2)}
          </pre>
        </section>
      )}

      {/* Study tools */}
      <footer className="study-tools">
        <div className="study-tools-heading">
          <h3>Study Tools</h3>
          <p>Turn your sources into study materials.</p>
        </div>

        <div className="study-tools-list">
          <button
            type="button"
            onClick={handleGenerateSummary}
            disabled={!selectedNotebook || studyToolLoading}
          >
            <span>📝</span>
            <strong>Summary</strong>
            <small>
              {studyToolLoading ? "Generating..." : "Summarize sources"}
            </small>
          </button>

          <button
            type="button"
            onClick={handleGenerateStudyGuide}
            disabled={!selectedNotebook || studyToolLoading}
          >
            <span>📚</span>
            <strong>Study Guide</strong>
            <small>
              {studyToolLoading ? "Generating..." : "Create study notes"}
            </small>
          </button>

          <button
            type="button"
            onClick={handleGenerateQuiz}
            disabled={!selectedNotebook || studyToolLoading}
          >
            <span>❓</span>
            <strong>Quiz</strong>
            <small>
              {studyToolLoading ? "Generating..." : "Test your knowledge"}
            </small>
          </button>
        </div>
      </footer>
    </div>
  );
}

export default App;