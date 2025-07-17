import React from 'react';
import { useAuthStore } from '../store/authStore';
import { 
  LogOut, 
  User, 
  BookOpen, 
  Users, 
  Settings,
  Home,
  FileText,
  GraduationCap
} from 'lucide-react';

interface LayoutProps {
  children: React.ReactNode;
}

const Layout: React.FC<LayoutProps> = ({ children }) => {
  const { user, logout } = useAuthStore();

  const navigationItems = [
    { name: '首页', href: '/', icon: Home, roles: ['admin', 'teacher', 'student'] },
    { name: '课程管理', href: '/courses', icon: BookOpen, roles: ['admin', 'teacher'] },
    { name: '实验管理', href: '/experiments', icon: FileText, roles: ['admin', 'teacher'] },
    { name: '班级管理', href: '/classes', icon: Users, roles: ['admin', 'teacher'] },
    { name: '我的课程', href: '/my-courses', icon: GraduationCap, roles: ['student'] },
    { name: '我的实验', href: '/my-experiments', icon: FileText, roles: ['student'] },
    { name: '用户管理', href: '/users', icon: User, roles: ['admin'] },
    { name: '系统设置', href: '/settings', icon: Settings, roles: ['admin'] },
  ];

  const filteredNavigation = navigationItems.filter(item => 
    user?.role && item.roles.includes(user.role)
  );

  const handleLogout = () => {
    logout();
    window.location.href = '/login';
  };

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      {/* Navigation */}
      <nav className="bg-white dark:bg-gray-800 shadow-sm border-b border-gray-200 dark:border-gray-700">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex">
              <div className="flex-shrink-0 flex items-center">
                <h1 className="text-xl font-bold text-gray-900 dark:text-white">
                  高校在线实验管理系统
                </h1>
              </div>
              <div className="hidden sm:ml-6 sm:flex sm:space-x-8">
                {filteredNavigation.map((item) => {
                  const Icon = item.icon;
                  return (
                    <a
                      key={item.name}
                      href={item.href}
                      className="inline-flex items-center px-1 pt-1 border-b-2 border-transparent text-sm font-medium text-gray-500 hover:text-gray-700 hover:border-gray-300 dark:text-gray-300 dark:hover:text-gray-100"
                    >
                      <Icon className="h-4 w-4 mr-2" />
                      {item.name}
                    </a>
                  );
                })}
              </div>
            </div>
            <div className="flex items-center">
              <div className="flex items-center space-x-4">
                <span className="text-sm text-gray-700 dark:text-gray-300">
                  {user?.username} ({user?.role === 'admin' ? '管理员' : user?.role === 'teacher' ? '教师' : '学生'})
                </span>
                <button
                  onClick={handleLogout}
                  className="inline-flex items-center px-3 py-2 border border-transparent text-sm leading-4 font-medium rounded-md text-gray-500 hover:text-gray-700 dark:text-gray-300 dark:hover:text-gray-100"
                >
                  <LogOut className="h-4 w-4 mr-2" />
                  退出
                </button>
              </div>
            </div>
          </div>
        </div>
      </nav>

      {/* Main content */}
      <main className="mx-auto max-w-7xl py-6 px-4 sm:px-6 lg:px-8">
        {children}
      </main>
    </div>
  );
};

export default Layout;