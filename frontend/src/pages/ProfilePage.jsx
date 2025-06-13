// ProfilePage.jsx
import React from 'react';
import { useAuth } from '../constants/AuthContext';

const ProfilePage = () => {

  const { user } = useAuth();

  if (!user) {
    return <div className="p-8"><h1>No user data available. Please log in.</h1></div>;
  }
  
  return (
    <div className="p-8 max-w-2xl mx-auto">
      <h1 className="text-3xl font-bold mb-6">User Profile</h1>
      <div className="card bg-base-100 shadow-xl">
        <div className="card-body">
          <p><strong>Email:</strong> {user.email}</p>
          <p><strong>First Name:</strong> {user.firstName || 'N/A'}</p>
          <p><strong>Last Name:</strong> {user.lastName || 'N/A'}</p>
          <p><strong>Subscription Plan:</strong> {user.plan}</p>
        </div>
      </div>
    </div>
  );
};

export default ProfilePage;