import axios from "axios";

const api = axios.create({
  baseURL: "http://127.0.0.1:8000",
});

export const getNotebooks = async () => {
  const response = await api.get("/notebooks");
  return response.data;
};

export const createNotebook = async (notebookData) => {
  const response = await api.post("/notebooks", notebookData);
  return response.data;
};

export const updateNotebook = async (notebookId, notebookData) => {
  const response = await api.patch(
    `/notebooks/${notebookId}`,
    notebookData
  );
  return response.data;
};

export const deleteNotebook = async (notebookId) => {
  const response = await api.delete(`/notebooks/${notebookId}`);
  return response.data;
};

export const getDocuments = async (notebookId) => {
  const response = await api.get(`/notebooks/${notebookId}/documents`);
  return response.data;
};

export const uploadDocument = async (notebookId, file) => {
  const formData = new FormData();
  formData.append("file", file);

  const response = await api.post(
    `/notebooks/${notebookId}/documents`,
    formData
  );

  return response.data;
};

export const addWebsite = async (notebookId, url) => {
  const response = await api.post(
    `/notebooks/${notebookId}/documents/url`,
    { url }
  );

  return response.data;
};

export const askQuestion = async (notebookId, question) => {
  const response = await api.post(
    `/notebooks/${notebookId}/ask`,
    { question }
  );

  return response.data;
};

export const getChatMessages = async (notebookId) => {
  const response = await api.get(`/notebooks/${notebookId}/messages`);
  return response.data;
};

export const generateSummary = async (notebookId) => {
  const response = await api.post(`/notebooks/${notebookId}/summary`);
  return response.data;
};

export const generateStudyGuide = async (notebookId) => {
  const response = await api.post(
    `/notebooks/${notebookId}/study-guide`
  );

  return response.data;
};

export const generateQuiz = async (notebookId, numQuestions = 5) => {
  const response = await api.post(
    `/notebooks/${notebookId}/quiz`,
    { num_questions: numQuestions }
  );

  return response.data;
};