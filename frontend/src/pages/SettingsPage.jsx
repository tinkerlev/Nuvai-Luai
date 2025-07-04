// SettingsPage.jsx
import React, { useState, useRef, useEffect } from 'react';
import { useAuth } from '../constants/AuthContext';

const ProfilePictureSettings = () => {
    const { user, setUser } = useAuth();
    const [isUploading, setIsUploading] = useState(false);
    const [isDeleting, setIsDeleting] = useState(false);
    const [error, setError] = useState('');
    const fileInputRef = useRef(null);
    const isMounted = useRef(false);

    useEffect(() => {
        isMounted.current = true;
        return () => {
            isMounted.current = false;
        };
    }, []);

    const handleFileChange = async (event) => {
        const file = event.target.files[0];
        if (!file) return;

        setError('');
        setIsUploading(true);
        const formData = new FormData();
        formData.append('profile_picture', file);

        try {
            const uploadResponse = await fetch(`${process.env.REACT_APP_API_URL}/auth/update-profile-picture`, {
                method: 'POST',
                body: formData,
                credentials: 'include'
            });
            
            const uploadData = await uploadResponse.json();
            if (!uploadResponse.ok) {
                throw new Error(uploadData.msg || 'Upload failed');
            }

            if (isMounted.current) {
                setUser(prevUser => {
                    const updatedUser = { ...prevUser, logoUrl: uploadData.newLogoUrl };
                    return updatedUser;
                });
            }
        } catch (err) {
            if (isMounted.current) {
                setError(err.message);
            }
        } finally {
            if (isMounted.current) {
                setIsUploading(false);
            }
        }
    };

        const handleDeletePicture = async () => {
        if (isUploading || isDeleting) return;

        setIsDeleting(true);
        setError('');

        try {
            const response = await fetch(`${process.env.REACT_APP_API_URL}/auth/delete-profile-picture`, {
                method: 'POST',
                credentials: 'include'
            });

            const data = await response.json();
            if (!response.ok) {
                throw new Error(data.error || 'Failed to delete picture.');
            }

            if (isMounted.current) {
                setUser(prevUser => ({
                    ...prevUser,
                    logoUrl: null
                }));
            }
        } catch (err) {
            if (isMounted.current) {
                setError(err.message);
            }
        } finally {
            if (isMounted.current) {
                setIsDeleting(false);
            }
        }
    };

    return (
        <div className="card bg-base-200 p-6 shadow-md">
            <h2 className="text-xl font-bold mb-4">Profile Picture</h2>
            <div className="flex items-center gap-6">
                <div className="avatar">
                    <div className="w-24 h-24 rounded-full ring ring-primary ring-offset-base-100 ring-offset-2 bg-neutral text-neutral-content">
                        {user?.logoUrl && !user.logoUrl.includes("default_logo") ? (
                            <img src={`${process.env.REACT_APP_API_URL}${user.logoUrl}`} alt="Profile" className="w-full h-full object-cover" />
                        ) : (
                            <div className="w-full h-full flex items-center justify-center">
                                <span className="text-3xl font-bold">
                                    {user?.initials ? user.initials.substring(0, 2).toUpperCase() : "??"}
                                </span>
                            </div>
                        )}
                    </div>
                </div>
                <div>
                    <input type="file" ref={fileInputRef} onChange={handleFileChange} accept="image/*" className="hidden" disabled={isUploading || isDeleting} />
                    <div className="flex flex-col gap-2">
                        <button onClick={() => fileInputRef.current.click()} className={`btn btn-primary ${isUploading ? "loading" : ""}`} disabled={isUploading || isDeleting}>Change Picture</button>
                        <p className="text-xs text-base-content/60 mt-2">.png, .jpg, .gif up to 2MB</p>
                        {user?.logoUrl && (

                            <button onClick={handleDeletePicture} className={`btn btn-error btn-outline ${isDeleting ? "loading" : ""}`} disabled={isUploading || isDeleting}>
                                Delete
                            </button>
                        )}
                </div>
                </div>
            </div>
            {error && <div className="text-error mt-2">{error}</div>}
        </div>
    );
};

const ProfileSettings = () => {
    const { user, setUser } = useAuth();    
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState('');
    const [success, setSuccess] = useState('');
    const [formData, setFormData] = useState({
        first_name: user?.firstName || '',
        last_name: user?.lastName || '',
        phone: user?.phone || '',
        profession: user?.profession || '',
        company: user?.company || '',
    });
    const isMounted = useRef(false);

    useEffect(() => {
        isMounted.current = true;
        return () => {
            isMounted.current = false;
        };
    }, []);

    const handleChange = (e) => {
        setFormData({ ...formData, [e.target.name]: e.target.value });
    };
    const handleSubmit = async (e) => {
        e.preventDefault();
        setIsLoading(true); setError(''); setSuccess('');
        try {
            const response = await fetch(`${process.env.REACT_APP_API_URL}/auth/update-profile`, {
                method: 'POST', headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(formData), credentials: 'include'
            });
            const data = await response.json();
            if (!response.ok) throw new Error(data.error || 'Failed to update profile.');
            if (isMounted.current) {
                    setSuccess('Profile updated successfully!');
                    setUser(prevUser => ({ ...prevUser, ...data.user }));
                }
            } catch (err) { 
                if (isMounted.current) {
                    setError(err.message);
                }
            } finally { 
                if (isMounted.current) {
                    setIsLoading(false);
                }
            }
    };

    return (
        <div className="card bg-base-200 p-6 shadow-md">
            <h2 className="text-xl font-bold mb-4">Personal Information</h2>
            <form onSubmit={handleSubmit} className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                        <label htmlFor="first_name" className="label-text font-medium">First Name</label>
                        <input type="text" name="first_name" value={formData.first_name} onChange={handleChange} className="input input-bordered w-full mt-1" />
                    </div>
                    <div>
                        <label htmlFor="last_name" className="label-text font-medium">Last Name</label>
                        <input type="text" name="last_name" value={formData.last_name} onChange={handleChange} className="input input-bordered w-full mt-1" />
                    </div>
                </div>
                <div><label htmlFor="phone" className="label-text font-medium">Phone</label><input type="tel" name="phone" value={formData.phone} onChange={handleChange} className="input input-bordered w-full mt-1" /></div>
                <div><label htmlFor="profession" className="label-text font-medium">Profession</label><input type="text" name="profession" value={formData.profession} onChange={handleChange} className="input input-bordered w-full mt-1" /></div>
                <div><label htmlFor="company" className="label-text font-medium">Company</label><input type="text" name="company" value={formData.company} onChange={handleChange} className="input input-bordered w-full mt-1" /></div>
                
                {success && <div className="alert alert-success shadow-lg"><div><span>{success}</span></div></div>}
                {error && <div className="alert alert-error shadow-lg"><div><span>{error}</span></div></div>}

                <div className="pt-2">
                    <button type="submit" className={`btn btn-primary ${isLoading ? "loading" : ""}`} disabled={isLoading}>Save Changes</button>
                </div>
            </form>
        </div>
    );
};

const SettingsPage = () => {
    const [activeTab, setActiveTab] = useState('profile');
    const renderTabContent = () => {
        switch(activeTab) {
            case 'profile': return <ProfileSettings />;
            case 'picture': return <ProfilePictureSettings />;
            case 'subscription': return <div>Subscription Management UI</div>;
            case 'scanner': return <div>Scanner Preferences UI</div>;
            default: return <ProfileSettings />;
        }
    };
    return (
        <div className="p-8 max-w-4xl mx-auto">
            <h1 className="text-3xl font-bold mb-8">Settings</h1>
            <div role="tablist" className="tabs tabs-boxed mb-6">
                <button role="tab" className={`tab ${activeTab === 'profile' ? 'tab-active' : ''}`} onClick={() => setActiveTab('profile')}>Details</button> 
                <button role="tab" className={`tab ${activeTab === 'picture' ? 'tab-active' : ''}`} onClick={() => setActiveTab('picture')}>Picture</button>
                <button role="tab" className={`tab ${activeTab === 'subscription' ? 'tab-active' : ''}`} onClick={() => setActiveTab('subscription')}>Subscription</button> 
                <button role="tab" className={`tab ${activeTab === 'scanner' ? 'tab-active' : ''}`} onClick={() => setActiveTab('scanner')}>Scanner</button>
            </div>
            <div>{renderTabContent()}</div>
        </div>
    );
};
export default SettingsPage;