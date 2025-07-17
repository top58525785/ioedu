import React, { useEffect, useState } from 'react';
import { useAuthStore } from '../store/authStore';
import { coursesApi, experimentsApi, classesApi, submissionsApi } from '../services/api';
import { BookOpen, FileText, Users, CheckCircle, Clock, AlertCircle } from 'lucide-react';
import Layout from '../components/Layout';

const Dashboard: React.FC = () => {
  const { user } = useAuthStore();
  const [stats, setStats] = useState({
    courses: 0,
    experiments: 0,
    classes: 0,
    submissions: 0,
    pendingSubmissions: 0,
    completedSubmissions: 0,
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchStats();
  }, [user]);

  const fetchStats = async () => {
    try {
      const promises = [];

      if (user?.role === 'admin') {
        promises.push(
          coursesApi.getCourses({ per_page: 1 }),
          experimentsApi.getExperiments({ per_page: 1 }),
          classesApi.getClasses({ per_page: 1 }),
          submissionsApi.getSubmissions({ per_page: 1 })
        );
      } else if (user?.role === 'teacher') {
        promises.push(
          coursesApi.getCourses({ per_page: 1 }),
          experimentsApi.getExperiments({ per_page: 1 }),
          classesApi.getClasses({ per_page: 1 }),
          submissionsApi.getSubmissions({ per_page: 1, status: 'submitted' }),
          submissionsApi.getSubmissions({ per_page: 1, status: 'graded' })
        );
      } else {
        promises.push(
          experimentsApi.getExperiments({ per_page: 1 }),
          submissionsApi.getSubmissions({ per_page: 1 }),
          submissionsApi.getSubmissions({ per_page: 1, status: 'graded' })
        );
      }

      const results = await Promise.all(promises);

      if (user?.role === 'admin') {
        setStats({
          courses: results[0].data.total,
          experiments: results[1].data.total,
          classes: results[2].data.total,
          submissions: results[3].data.total,
          pendingSubmissions: 0,
          completedSubmissions: 0,
        });
      } else if (user?.role === 'teacher') {
        setStats({
          courses: results[0].data.total,
          experiments: results[1].data.total,
          classes: results[2].data.total,
          submissions: 0,
          pendingSubmissions: results[3].data.total,
          completedSubmissions: results[4].data.total,
        });
      } else {
        setStats({
          courses: 0,
          experiments: results[0].data.total,
          classes: 0,
          submissions: results[1].data.total,
          pendingSubmissions: 0,
          completedSubmissions: results[2].data.total,
        });
      }
    } catch (error) {
      console.error('Failed to fetch stats:', error);
    } finally {
      setLoading(false);
    }
  };

  const getStatsCards = () => {
    if (user?.role === 'admin') {
      return [
        { name: '课程总数', value: stats.courses, icon: BookOpen, color: 'bg-blue-500' },
        { name: '实验总数', value: stats.experiments, icon: FileText, color: 'bg-green-500' },
        { name: '班级总数', value: stats.classes, icon: Users, color: 'bg-purple-500' },
        { name: '提交总数', value: stats.submissions, icon: CheckCircle, color: 'bg-orange-500' },
      ];
    } else if (user?.role === 'teacher') {
      return [
        { name: '我的课程', value: stats.courses, icon: BookOpen, color: 'bg-blue-500' },
        { name: '我的实验', value: stats.experiments, icon: FileText, color: 'bg-green-500' },
        { name: '我的班级', value: stats.classes, icon: Users, color: 'bg-purple-500' },
        { name: '待批改', value: stats.pendingSubmissions, icon: Clock, color: 'bg-yellow-500' },
        { name: '已批改', value: stats.completedSubmissions, icon: CheckCircle, color: 'bg-green-500' },
      ];
    } else {
      return [
        { name: '可做实验', value: stats.experiments, icon: FileText, color: 'bg-green-500' },
        { name: '我的提交', value: stats.submissions, icon: CheckCircle, color: 'bg-blue-500' },
        { name: '已完成', value: stats.completedSubmissions, icon: CheckCircle, color: 'bg-green-500' },
      ];
    }
  };

  if (loading) {
    return (
      <Layout>
        <div className="flex justify-center items-center h-64">
          <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600"></div>
        </div>
      </Layout>
    );
  }

  return (
    <Layout>
      <div className="space-y-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
            欢迎回来，{user?.username}
          </h1>
          <p className="text-gray-600 dark:text-gray-400">
            {user?.role === 'admin' ? '系统管理员' : 
             user?.role === 'teacher' ? '教师' : '学生'} - 
            这里是您的工作台
          </p>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
          {getStatsCards().map((item) => {
            const Icon = item.icon;
            return (
              <div key={item.name} className="card">
                <div className="flex items-center">
                  <div className={`p-2 rounded-md ${item.color}`}>
                    <Icon className="h-6 w-6 text-white" />
                  </div>
                  <div className="ml-4">
                    <p className="text-sm font-medium text-gray-500 dark:text-gray-400">
                      {item.name}
                    </p>
                    <p className="text-2xl font-semibold text-gray-900 dark:text-white">
                      {item.value}
                    </p>
                  </div>
                </div>
              </div>
            );
          })}
        </div>

        {/* Quick Actions */}
        <div className="card">
          <h2 className="text-lg font-medium text-gray-900 dark:text-white mb-4">
            快速操作
          </h2>
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {user?.role === 'admin' && (
              <>
                <a
                  href="/users"
                  className="flex items-center p-4 bg-gray-50 dark:bg-gray-700 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-600 transition-colors"
                >
                  <Users className="h-8 w-8 text-blue-600 mr-3" />
                  <div>
                    <p className="font-medium text-gray-900 dark:text-white">用户管理</p>
                    <p className="text-sm text-gray-500 dark:text-gray-400">管理系统用户</p>
                  </div>
                </a>
                <a
                  href="/courses"
                  className="flex items-center p-4 bg-gray-50 dark:bg-gray-700 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-600 transition-colors"
                >
                  <BookOpen className="h-8 w-8 text-green-600 mr-3" />
                  <div>
                    <p className="font-medium text-gray-900 dark:text-white">课程管理</p>
                    <p className="text-sm text-gray-500 dark:text-gray-400">管理所有课程</p>
                  </div>
                </a>
              </>
            )}
            {user?.role === 'teacher' && (
              <>
                <a
                  href="/courses"
                  className="flex items-center p-4 bg-gray-50 dark:bg-gray-700 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-600 transition-colors"
                >
                  <BookOpen className="h-8 w-8 text-blue-600 mr-3" />
                  <div>
                    <p className="font-medium text-gray-900 dark:text-white">我的课程</p>
                    <p className="text-sm text-gray-500 dark:text-gray-400">管理我的课程</p>
                  </div>
                </a>
                <a
                  href="/experiments"
                  className="flex items-center p-4 bg-gray-50 dark:bg-gray-700 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-600 transition-colors"
                >
                  <FileText className="h-8 w-8 text-green-600 mr-3" />
                  <div>
                    <p className="font-medium text-gray-900 dark:text-white">实验管理</p>
                    <p className="text-sm text-gray-500 dark:text-gray-400">创建和管理实验</p>
                  </div>
                </a>
                <a
                  href="/classes"
                  className="flex items-center p-4 bg-gray-50 dark:bg-gray-700 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-600 transition-colors"
                >
                  <Users className="h-8 w-8 text-purple-600 mr-3" />
                  <div>
                    <p className="font-medium text-gray-900 dark:text-white">班级管理</p>
                    <p className="text-sm text-gray-500 dark:text-gray-400">管理我的班级</p>
                  </div>
                </a>
              </>
            )}
            {user?.role === 'student' && (
              <>
                <a
                  href="/my-experiments"
                  className="flex items-center p-4 bg-gray-50 dark:bg-gray-700 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-600 transition-colors"
                >
                  <FileText className="h-8 w-8 text-blue-600 mr-3" />
                  <div>
                    <p className="font-medium text-gray-900 dark:text-white">我的实验</p>
                    <p className="text-sm text-gray-500 dark:text-gray-400">查看和完成实验</p>
                  </div>
                </a>
                <a
                  href="/my-courses"
                  className="flex items-center p-4 bg-gray-50 dark:bg-gray-700 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-600 transition-colors"
                >
                  <BookOpen className="h-8 w-8 text-green-600 mr-3" />
                  <div>
                    <p className="font-medium text-gray-900 dark:text-white">我的课程</p>
                    <p className="text-sm text-gray-500 dark:text-gray-400">查看课程信息</p>
                  </div>
                </a>
              </>
            )}
          </div>
        </div>
      </div>
    </Layout>
  );
};

export default Dashboard;