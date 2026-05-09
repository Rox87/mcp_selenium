import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Settings, Plus, Trash2, Edit2, Save, X } from 'lucide-react';

const API_URL = 'http://localhost:8000';

function App() {
  const [profiles, setProfiles] = useState([]);
  const [editingProfile, setEditingProfile] = useState(null);
  const [isCreating, setIsCreating] = useState(false);
  const [loading, setLoading] = useState(true);

  const emptyProfile = {
    id: '',
    name: '',
    headless: true,
    disable_images: false,
    user_data_dir: '',
    user_agent: '',
    proxy: ''
  };

  const [formData, setFormData] = useState(emptyProfile);

  useEffect(() => {
    fetchProfiles();
  }, []);

  const fetchProfiles = async () => {
    try {
      const response = await axios.get(`${API_URL}/profiles`);
      setProfiles(response.data);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching profiles:', error);
      setLoading(false);
    }
  };

  const handleInputChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData({
      ...formData,
      [name]: type === 'checkbox' ? checked : value
    });
  };

  const startCreate = () => {
    setFormData({ ...emptyProfile, id: `profile_${Date.now()}` });
    setIsCreating(true);
    setEditingProfile(null);
  };

  const startEdit = (profile) => {
    setFormData({
      ...profile,
      user_data_dir: profile.user_data_dir || '',
      user_agent: profile.user_agent || '',
      proxy: profile.proxy || ''
    });
    setEditingProfile(profile.id);
    setIsCreating(false);
  };

  const cancelEdit = () => {
    setEditingProfile(null);
    setIsCreating(false);
    setFormData(emptyProfile);
  };

  const saveProfile = async (e) => {
    e.preventDefault();
    try {
      const payload = {
        ...formData,
        user_data_dir: formData.user_data_dir || null,
        user_agent: formData.user_agent || null,
        proxy: formData.proxy || null
      };

      if (isCreating) {
        await axios.post(`${API_URL}/profiles`, payload);
      } else {
        await axios.put(`${API_URL}/profiles/${formData.id}`, payload);
      }

      await fetchProfiles();
      cancelEdit();
    } catch (error) {
      console.error('Error saving profile:', error);
      alert('Error saving profile. Check console for details.');
    }
  };

  const deleteProfile = async (id) => {
    if (window.confirm('Are you sure you want to delete this profile?')) {
      try {
        await axios.delete(`${API_URL}/profiles/${id}`);
        await fetchProfiles();
      } catch (error) {
        console.error('Error deleting profile:', error);
      }
    }
  };

  return (
    <div className="min-h-screen bg-gray-100 p-8">
      <div className="max-w-4xl mx-auto">
        <header className="flex justify-between items-center mb-8 bg-white p-6 rounded-lg shadow-sm">
          <div className="flex items-center gap-3">
            <Settings className="w-8 h-8 text-blue-600" />
            <h1 className="text-2xl font-bold text-gray-800">Selenium MCP Profiles</h1>
          </div>
          {!isCreating && !editingProfile && (
            <button
              onClick={startCreate}
              className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-md transition-colors"
            >
              <Plus className="w-4 h-4" />
              New Profile
            </button>
          )}
        </header>

        {(isCreating || editingProfile) ? (
          <div className="bg-white p-6 rounded-lg shadow-md mb-8">
            <h2 className="text-xl font-semibold mb-4 border-b pb-2">
              {isCreating ? 'Create New Profile' : 'Edit Profile'}
            </h2>
            <form onSubmit={saveProfile} className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="col-span-2 md:col-span-1">
                  <label className="block text-sm font-medium text-gray-700 mb-1">Profile ID (Identifier)</label>
                  <input
                    type="text"
                    name="id"
                    value={formData.id}
                    onChange={handleInputChange}
                    disabled={!isCreating}
                    required
                    className="w-full p-2 border border-gray-300 rounded-md bg-gray-50 disabled:text-gray-500"
                  />
                </div>
                <div className="col-span-2 md:col-span-1">
                  <label className="block text-sm font-medium text-gray-700 mb-1">Profile Name (Display)</label>
                  <input
                    type="text"
                    name="name"
                    value={formData.name}
                    onChange={handleInputChange}
                    required
                    className="w-full p-2 border border-gray-300 rounded-md"
                    placeholder="e.g., My Scraping Profile"
                  />
                </div>

                <div className="col-span-2 space-y-3 p-4 bg-gray-50 rounded-md border border-gray-200">
                  <h3 className="font-medium text-gray-800">Browser Behavior</h3>
                  <div className="flex items-center gap-2">
                    <input
                      type="checkbox"
                      id="headless"
                      name="headless"
                      checked={formData.headless}
                      onChange={handleInputChange}
                      className="w-4 h-4 text-blue-600 rounded"
                    />
                    <label htmlFor="headless" className="text-sm text-gray-700">Headless Mode (Invisible)</label>
                  </div>
                  <div className="flex items-center gap-2">
                    <input
                      type="checkbox"
                      id="disable_images"
                      name="disable_images"
                      checked={formData.disable_images}
                      onChange={handleInputChange}
                      className="w-4 h-4 text-blue-600 rounded"
                    />
                    <label htmlFor="disable_images" className="text-sm text-gray-700">Disable Images (Faster)</label>
                  </div>
                </div>

                <div className="col-span-2">
                  <label className="block text-sm font-medium text-gray-700 mb-1">User Data Directory (Optional)</label>
                  <input
                    type="text"
                    name="user_data_dir"
                    value={formData.user_data_dir}
                    onChange={handleInputChange}
                    className="w-full p-2 border border-gray-300 rounded-md"
                    placeholder="/path/to/chrome/profile"
                  />
                </div>

                <div className="col-span-2 md:col-span-1">
                  <label className="block text-sm font-medium text-gray-700 mb-1">Custom User-Agent (Optional)</label>
                  <input
                    type="text"
                    name="user_agent"
                    value={formData.user_agent}
                    onChange={handleInputChange}
                    className="w-full p-2 border border-gray-300 rounded-md"
                    placeholder="Mozilla/5.0..."
                  />
                </div>

                <div className="col-span-2 md:col-span-1">
                  <label className="block text-sm font-medium text-gray-700 mb-1">Proxy Server (Optional)</label>
                  <input
                    type="text"
                    name="proxy"
                    value={formData.proxy}
                    onChange={handleInputChange}
                    className="w-full p-2 border border-gray-300 rounded-md"
                    placeholder="http://proxy.example.com:8080"
                  />
                </div>
              </div>

              <div className="flex justify-end gap-3 pt-4 mt-4 border-t">
                <button
                  type="button"
                  onClick={cancelEdit}
                  className="flex items-center gap-2 px-4 py-2 text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50"
                >
                  <X className="w-4 h-4" /> Cancel
                </button>
                <button
                  type="submit"
                  className="flex items-center gap-2 px-4 py-2 text-white bg-blue-600 rounded-md hover:bg-blue-700"
                >
                  <Save className="w-4 h-4" /> Save Profile
                </button>
              </div>
            </form>
          </div>
        ) : null}

        <div className="bg-white rounded-lg shadow-sm overflow-hidden">
          {loading ? (
            <div className="p-8 text-center text-gray-500">Loading profiles...</div>
          ) : profiles.length === 0 ? (
            <div className="p-8 text-center text-gray-500">No profiles found. Create one to get started.</div>
          ) : (
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="bg-gray-50 border-b border-gray-200">
                  <th className="p-4 font-semibold text-gray-600">Name</th>
                  <th className="p-4 font-semibold text-gray-600">ID</th>
                  <th className="p-4 font-semibold text-gray-600">Headless</th>
                  <th className="p-4 font-semibold text-gray-600">State</th>
                  <th className="p-4 font-semibold text-gray-600 text-right">Actions</th>
                </tr>
              </thead>
              <tbody>
                {profiles.map(profile => (
                  <tr key={profile.id} className="border-b border-gray-100 hover:bg-gray-50">
                    <td className="p-4 font-medium">{profile.name}</td>
                    <td className="p-4 text-gray-500 text-sm font-mono">{profile.id}</td>
                    <td className="p-4">
                      <span className={`px-2 py-1 rounded-full text-xs ${profile.headless ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'}`}>
                        {profile.headless ? 'Yes' : 'No'}
                      </span>
                    </td>
                    <td className="p-4 text-sm text-gray-600">
                      {profile.user_data_dir ? 'Persistent' : 'Ephemeral'}
                    </td>
                    <td className="p-4 flex justify-end gap-2">
                      <button
                        onClick={() => startEdit(profile)}
                        className="p-2 text-blue-600 hover:bg-blue-50 rounded"
                      >
                        <Edit2 className="w-4 h-4" />
                      </button>
                      <button
                        onClick={() => deleteProfile(profile.id)}
                        className="p-2 text-red-600 hover:bg-red-50 rounded"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      </div>
    </div>
  );
}

export default App;
