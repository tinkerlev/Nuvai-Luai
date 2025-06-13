// UserMenu.jsx
import React from 'react';
import { useAuth } from '../constants/AuthContext';
import { useNavigate } from 'react-router-dom';

const UserMenu = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };  
  if (!user) return null;

  return (
    <div className="dropdown dropdown-end">
      <label tabIndex={0} className="btn btn-ghost btn-circle avatar">
        <div className="w-10 rounded-full">
          <img src={user.logoUrl} alt="User Profile" referrerPolicy="no-referrer" />
        </div>
      </label>
      <ul tabIndex={0} className="menu menu-compact dropdown-content mt-3 p-2 shadow bg-base-100 rounded-box w-52 z-50">
        <li className="p-2">
          <p className="font-bold">{user.fullName}</p>
          <p className="text-xs text-base-content/70">{user.email}</p>
        </li>
        <li><div className="divider my-0"></div></li>
        <li><button to="/profile" onClick={() => document.activeElement.blur()}> Profile </button></li>
        <li><button to="/settings" onClick={() => document.activeElement.blur()}> Settings </button></li>
        <li><div className="divider my-0"></div></li>
        <li><button onClick={handleLogout}> Logout </button></li>
      </ul>
    </div>
  );
};

export default UserMenu;