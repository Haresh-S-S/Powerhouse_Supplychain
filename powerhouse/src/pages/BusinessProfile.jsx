import React, { useState } from 'react';
import {
  Pencil,
  Save,
  X
} from 'lucide-react';
import Button from '../components/ui/Button';
import ProfileCompletion from '../components/business-profile/ProfileCompletion';
import BusinessInformation from '../components/business-profile/BusinessInformation';
import BusinessLocation from '../components/business-profile/BusinessLocation';
import BusinessOperations from '../components/business-profile/BusinessOperations';
import RegistrationDetails from '../components/business-profile/RegistrationDetails';
import BusinessSummary from '../components/business-profile/BusinessSummary';
import ProfileStatus from '../components/business-profile/ProfileStatus';
import BusinessIntelligencePreview from '../components/business-profile/BusinessIntelligencePreview';
import { useBusinessAnalysis } from '../context/BusinessAnalysisContext';

export default function BusinessProfile({ showToast, setModalState, onNavigate }) {
  const { businessProfile, updateBusinessProfile, runAnalysis, isAnalyzing } = useBusinessAnalysis();
  const [profileData, setProfileData] = useState(businessProfile);
  const [tempData, setTempData] = useState(businessProfile);
  const [isEditing, setIsEditing] = useState(false);

  const handleEditClick = () => {
    setTempData({ ...profileData });
    setIsEditing(true);
  };

  const handleCancel = () => {
    setTempData({ ...profileData });
    setIsEditing(false);
    showToast('Editing cancelled. Original profile restored.');
  };

  const handleSave = () => {
    setProfileData({ ...tempData });
    updateBusinessProfile(tempData);
    setIsEditing(false);
    showToast('Business Profile successfully updated! Analysis engine resynced.');
  };

  const handleFieldChange = (e) => {
    const { name, value } = e.target;
    setTempData((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const handleViewAnalysis = async () => {
    showToast('Running Business Analysis Engine...');
    await runAnalysis(profileData, () => {
      if (onNavigate) {
        onNavigate('business-analysis');
      }
    });
  };

  const currentData = isEditing ? tempData : profileData;

  return (
    <div className="space-y-6">
      {/* Top Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-1">
        <div>
          <h1 className="text-xl sm:text-2xl font-bold text-slate-900 tracking-tight">
            Business Profile
          </h1>
          <p className="text-xs sm:text-sm text-slate-500 mt-0.5">
            Manage your business information to receive personalized compliance recommendations.
          </p>
        </div>

        {/* Edit / Save / Cancel Buttons */}
        <div className="flex items-center gap-2 self-start sm:self-auto">
          {isEditing ? (
            <>
              <Button
                variant="secondary"
                size="sm"
                onClick={handleCancel}
                className="text-xs font-semibold"
              >
                <X className="w-3.5 h-3.5" />
                <span>Cancel</span>
              </Button>
              <Button
                variant="primary"
                size="sm"
                onClick={handleSave}
                className="text-xs font-semibold"
              >
                <Save className="w-3.5 h-3.5" />
                <span>Save Changes</span>
              </Button>
            </>
          ) : (
            <Button
              variant="primary"
              size="sm"
              onClick={handleEditClick}
              className="text-xs font-semibold"
            >
              <Pencil className="w-3.5 h-3.5" />
              <span>Edit Profile</span>
            </Button>
          )}
        </div>
      </div>

      {/* Profile Completion Action Card */}
      <ProfileCompletion
        completionPercentage={85}
        remainingItems={2}
        onCompleteClick={() => {
          handleEditClick();
          showToast('Form fields highlighted for remaining items.');
        }}
      />

      {/* Main Two-Column Layout */}
      {/* Desktop: Left 68% / Right 32% */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
        {/* Left Column: Main Business Information Sections */}
        <div className="lg:col-span-8 space-y-6">
          {/* Section 1: Business Information */}
          <BusinessInformation
            data={currentData}
            isEditing={isEditing}
            onChange={handleFieldChange}
          />

          {/* Section 2: Business Location */}
          <BusinessLocation
            data={currentData}
            isEditing={isEditing}
            onChange={handleFieldChange}
          />

          {/* Section 3: Business Operations */}
          <BusinessOperations
            data={currentData}
            isEditing={isEditing}
            onChange={handleFieldChange}
          />

          {/* Section 4: Registration Details */}
          <RegistrationDetails
            data={currentData}
            isEditing={isEditing}
            onChange={handleFieldChange}
          />
        </div>

        {/* Right Column: Summary & Status Cards */}
        <div className="lg:col-span-4 space-y-6">
          {/* Business Summary Card */}
          <BusinessSummary data={currentData} />

          {/* Profile Status Card */}
          <ProfileStatus completionPercentage={85} />

          {/* AI Intelligence Preview Card */}
          <BusinessIntelligencePreview
            isAnalyzing={isAnalyzing}
            onViewAnalysis={handleViewAnalysis}
          />
        </div>
      </div>
    </div>
  );
}