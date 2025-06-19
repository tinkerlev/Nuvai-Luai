// UserMenu.jsx
import React from 'react';
import { useAuth } from '../constants/AuthContext';
import { useNavigate, Link } from 'react-router-dom';
import ThemeSwitcher from './ThemeSwitcher';

const UserMenu = () => {
  const { user, logout } = useAuth();
  const closeDropdown = () => document.activeElement.blur();
  const navigate = useNavigate();

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  return (
    <div className="dropdown dropdown-end">
      <label tabIndex={0} className="btn btn-ghost btn-circle avatar">
        <div className="w-10 h-10 rounded-full overflow-hidden">
          {user?.logoUrl && !user.logoUrl.includes('default_logo') ? (
            <img
              src={`${process.env.REACT_APP_API_URL}${user.logoUrl}`}
              alt="Avatar"
              className="w-full h-full object-cover"
            />
          ) : user ? (
            <div className="w-full h-full flex items-center justify-center bg-neutral-focus text-neutral-content ring ring-primary ring-offset-base-100 ring-offset-2">
              <span className="text-sm font-bold">
                {user?.initials?.substring(0, 2).toUpperCase() || '??'}
              </span>
            </div>
          ) : (
            <img
              src="/Logo-Luai-tr.svg"
              alt="Default Logo-Luai-tr"
              className="w-full h-full object-contain p-1"
            />
          )}
        </div>
      </label>

      <ul
        tabIndex={0}
        className="menu menu-compact dropdown-content mt-1 p-2 shadow bg-base-100 rounded-box w-52 z-50"
      >
        {user ? (
          <>
            <li className="p-2">
              <p className="font-bold">{user.fullName}</p>
              <p className="text-xs text-base-content/70 truncate">{user.email}</p>
            </li>
            <li><div className="divider my-0"></div></li>
            <li onClick={closeDropdown}><Link to="/Profile">Profile</Link></li>
            <li onClick={closeDropdown}><Link to="/settings">Settings</Link></li>
            <li><div className="divider my-0"></div></li>
            <li onClick={closeDropdown}><ThemeSwitcher onSelect={closeDropdown} /></li>
            <li><div className="divider my-0"></div></li>
            <li>
              <button
                onClick={handleLogout}
                className="text-error justify-start w-full"
              >
                Logout
              </button>
            </li>
          </>
        ) : (
          <>
            <li onClick={closeDropdown}><Link to="/login">Login</Link></li>
            <li onClick={closeDropdown}><Link to="/register">Register</Link></li>
            <li><div className="divider my-0"></div></li>
            <li onClick={closeDropdown}><ThemeSwitcher onSelect={closeDropdown} /></li>
          </>
        )}
      </ul>
    </div>
  );
};

export default UserMenu;
