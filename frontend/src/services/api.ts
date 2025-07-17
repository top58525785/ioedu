import axios from 'axios';
import type {
  User,
  Course,
  Experiment,
  Class,
  Submission,
  LoginRequest,
  LoginResponse,
  PaginationResponse,
} from '../types';

const API_BASE_URL = 'http://localhost:5000/api';

// 创建axios实例
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// 请求拦截器 - 添加认证token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// 响应拦截器 - 处理错误
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('access_token');
      localStorage.removeItem('user');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// 认证相关API
export const authApi = {
  login: (data: LoginRequest) =>
    api.post<LoginResponse>('/auth/login', data),
  
  register: (data: { username: string; email: string; password: string; role?: string }) =>
    api.post<{ message: string; user: User }>('/auth/register', data),
  
  getProfile: () =>
    api.get<{ user: User }>('/auth/profile'),
  
  changePassword: (data: { old_password: string; new_password: string }) =>
    api.put<{ message: string }>('/auth/change-password', data),
};

// 用户管理API
export const usersApi = {
  getUsers: (params?: {
    page?: number;
    per_page?: number;
    role?: string;
    search?: string;
  }) => api.get<PaginationResponse<User>>('/users', { params }),
  
  getUser: (id: number) =>
    api.get<{ user: User }>(`/users/${id}`),
  
  createUser: (data: {
    username: string;
    email: string;
    password: string;
    role: string;
  }) => api.post<{ message: string; user: User }>('/users', data),
  
  updateUser: (id: number, data: Partial<User>) =>
    api.put<{ message: string; user: User }>(`/users/${id}`, data),
  
  deleteUser: (id: number) =>
    api.delete<{ message: string }>(`/users/${id}`),
};

// 课程管理API
export const coursesApi = {
  getCourses: (params?: {
    page?: number;
    per_page?: number;
    search?: string;
    teacher_id?: number;
  }) => api.get<PaginationResponse<Course>>('/courses', { params }),
  
  getCourse: (id: number) =>
    api.get<{ course: Course }>(`/courses/${id}`),
  
  createCourse: (data: {
    name: string;
    code: string;
    description?: string;
    semester: string;
    teacher_id?: number;
  }) => api.post<{ message: string; course: Course }>('/courses', data),
  
  updateCourse: (id: number, data: Partial<Course>) =>
    api.put<{ message: string; course: Course }>(`/courses/${id}`, data),
  
  deleteCourse: (id: number) =>
    api.delete<{ message: string }>(`/courses/${id}`),
};

// 实验管理API
export const experimentsApi = {
  getExperiments: (params?: {
    page?: number;
    per_page?: number;
    course_id?: number;
    status?: string;
    search?: string;
  }) => api.get<PaginationResponse<Experiment>>('/experiments', { params }),
  
  getExperiment: (id: number) =>
    api.get<{ experiment: Experiment }>(`/experiments/${id}`),
  
  createExperiment: (data: {
    title: string;
    description?: string;
    instructions?: string;
    objectives?: string;
    requirements?: string;
    max_score?: number;
    course_id: number;
  }) => api.post<{ message: string; experiment: Experiment }>('/experiments', data),
  
  updateExperiment: (id: number, data: Partial<Experiment>) =>
    api.put<{ message: string; experiment: Experiment }>(`/experiments/${id}`, data),
  
  deleteExperiment: (id: number) =>
    api.delete<{ message: string }>(`/experiments/${id}`),
  
  addStep: (experimentId: number, data: {
    title: string;
    description?: string;
    expected_result?: string;
    scoring_criteria?: string;
    order?: number;
  }) => api.post(`/experiments/${experimentId}/steps`, data),
  
  addDataPoint: (experimentId: number, data: {
    name: string;
    type: string;
    unit?: string;
    is_required?: boolean;
    value_range?: string;
    options?: string;
  }) => api.post(`/experiments/${experimentId}/data-points`, data),
};

// 班级管理API
export const classesApi = {
  getClasses: (params?: {
    page?: number;
    per_page?: number;
    search?: string;
  }) => api.get<PaginationResponse<Class>>('/classes', { params }),
  
  getClass: (id: number) =>
    api.get<{ class: Class }>(`/classes/${id}`),
  
  createClass: (data: {
    name: string;
    description?: string;
    teacher_id?: number;
  }) => api.post<{ message: string; class: Class }>('/classes', data),
  
  updateClass: (id: number, data: Partial<Class>) =>
    api.put<{ message: string; class: Class }>(`/classes/${id}`, data),
  
  deleteClass: (id: number) =>
    api.delete<{ message: string }>(`/classes/${id}`),
  
  addStudent: (classId: number, data: { student_id: number }) =>
    api.post<{ message: string }>(`/classes/${classId}/students`, data),
  
  joinClass: (classId: number) =>
    api.post<{ message: string }>(`/classes/${classId}/join`),
};

// 实验提交API
export const submissionsApi = {
  getSubmissions: (params?: {
    page?: number;
    per_page?: number;
    experiment_id?: number;
    student_id?: number;
    status?: string;
  }) => api.get<PaginationResponse<Submission>>('/submissions', { params }),
  
  getSubmission: (id: number) =>
    api.get<{ submission: Submission }>(`/submissions/${id}`),
  
  createSubmission: (data: {
    experiment_id: number;
    content?: string;
    data_values?: string;
    files?: string;
  }) => api.post<{ message: string; submission: Submission }>('/submissions', data),
  
  updateSubmission: (id: number, data: Partial<Submission>) =>
    api.put<{ message: string; submission: Submission }>(`/submissions/${id}`, data),
  
  gradeSubmission: (id: number, data: {
    score: number;
    feedback?: string;
  }) => api.post<{ message: string; submission: Submission }>(`/submissions/${id}/grade`, data),
};

export default api;