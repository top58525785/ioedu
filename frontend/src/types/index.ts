export interface User {
  id: number;
  username: string;
  email: string;
  role: 'admin' | 'teacher' | 'student';
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface Course {
  id: number;
  name: string;
  code: string;
  description: string;
  teacher_id: number;
  teacher_name?: string;
  semester: string;
  status: 'active' | 'archived';
  created_at: string;
  updated_at: string;
}

export interface Experiment {
  id: number;
  title: string;
  description: string;
  instructions: string;
  objectives: string;
  requirements: string;
  max_score: number;
  course_id: number;
  course_name?: string;
  status: 'draft' | 'published' | 'active' | 'completed';
  created_at: string;
  updated_at: string;
  steps_count: number;
  data_points_count: number;
  steps?: ExperimentStep[];
  data_points?: DataPoint[];
}

export interface ExperimentStep {
  id: number;
  experiment_id: number;
  title: string;
  description: string;
  expected_result: string;
  scoring_criteria: string;
  order: number;
  created_at: string;
}

export interface DataPoint {
  id: number;
  experiment_id: number;
  name: string;
  type: 'number' | 'text' | 'select' | 'file';
  unit: string;
  is_required: boolean;
  value_range: string;
  options: string;
  created_at: string;
}

export interface Class {
  id: number;
  name: string;
  description: string;
  teacher_id: number;
  teacher_name?: string;
  student_count: number;
  created_at: string;
  updated_at: string;
  students?: User[];
}

export interface Submission {
  id: number;
  experiment_id: number;
  experiment_title?: string;
  student_id: number;
  student_name?: string;
  attempt_number: number;
  status: 'draft' | 'submitted' | 'graded';
  content: string;
  data_values: string;
  files: string;
  score?: number;
  feedback?: string;
  graded_by?: number;
  grader_name?: string;
  graded_at?: string;
  submitted_at?: string;
  created_at: string;
  updated_at: string;
}

export interface LoginRequest {
  username: string;
  password: string;
}

export interface LoginResponse {
  access_token: string;
  user: User;
}

export interface ApiResponse<T> {
  message?: string;
  data?: T;
}

export interface PaginationResponse<T> {
  items: T[];
  total: number;
  pages: number;
  current_page: number;
  per_page: number;
}