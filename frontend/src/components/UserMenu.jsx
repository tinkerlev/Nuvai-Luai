// UserMenu.jsx
import React from 'react';
import { useAuth } from '../constants/AuthContext';
import { useNavigate, Link } from 'react-router-dom';

const UserMenu = () => {
  const { user, logout } = useAuth();
  const closeDropdown = () => document.activeElement.blur();
  const navigate = useNavigate();
  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };  
  if (!user) return null;

  return (
    <div className="dropdown dropdown-end">
      <label tabIndex={0} className="btn btn-ghost btn-circle avatar">
        {user?.logoUrl && !user.logoUrl.includes("default_logo") ? (
          <div className="w-10 h-10 rounded-full overflow-hidden">
            <img 
            src={`${process.env.REACT_APP_API_URL}${user.logoUrl}`} 
            alt="Avatar" 
            className="w-full h-full object-cover"/>
          </div>
        ) : (
          <div className="w-10 h-10 rounded-full ring ring-primary ring-offset-base-100 ring-offset-2 bg-neutral-focus text-neutral-content overflow-hidden">
              <div className="w-full h-full flex items-center justify-center">
                  <span className="text-sm font-bold">
                      {user?.initials?.substring(0, 2).toUpperCase() || "??"}
                  </span>
              </div>
          </div>
        )}
      </label>
      <ul tabIndex={0} className="menu menu-compact dropdown-content mt-3 p-2 shadow bg-base-100 rounded-box w-52 z-50">
        <li className="p-2">
          <p className="font-bold">{user.fullName}</p>
          <p className="text-xs text-base-content/70 truncate">{user.email}</p>
        </li>
        <li><div className="divider my-0"></div></li>
         <li onClick={closeDropdown}>
            <Link to="/Profile">Profile</Link>
         </li>
         <li onClick={closeDropdown}>
            <Link to="/settings">Settings</Link>
         </li>
        <li><div className="divider my-0"></div></li>
        <li> <button onClick={handleLogout} className="text-error justify-start w-full">Logout</button> </li>
      </ul>
    </div>
  );
};

export default UserMenu;