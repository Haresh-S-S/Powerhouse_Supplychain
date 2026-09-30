import React from 'react';
import {
  Cog,
  Workflow,
  Factory,
  ArrowDownLeft,
  ArrowUpRight,
  Leaf,
  Activity
} from 'lucide-react';
import ProfileField from '../shared/ProfileField';
import Badge from '../ui/Badge';
import { profileOptions } from '../../data/businessProfileData';

export default function BusinessOperations({ data, isEditing, onChange }) {
  return (
    <div className="bg-[#111827] rounded-2xl border border-[#1E293B] shadow-2xs p-5 sm:p-6">
      {/* Header */}
      <div className="flex items-center gap-2.5 pb-4 border-b border-slate-800">
        <div className="p-1.5 rounded-lg bg-blue-950 text-blue-400 border border-blue-800">
          <Cog className="w-4 h-4" />
        </div>
        <div>
          <h3 className="text-base font-bold text-white leading-none">
            Business Operations
          </h3>
          <p className="text-xs text-slate-400 mt-1">
            Information about your business activities and operations.
          </p>
        </div>
      </div>

      {/* Fields */}
      <div className="mt-4 divide-y divide-slate-800/60">
        <ProfileField
          label="Primary Activity"
          value={data.primaryActivity}
          name="primaryActivity"
          isEditing={isEditing}
          onChange={onChange}
          icon={Workflow}
          placeholder="e.g. Retail Sale of Clothing & Textile Products"
        />

        <ProfileField
          label="Secondary Activities"
          value={data.secondaryActivities}
          name="secondaryActivities"
          isEditing={isEditing}
          onChange={onChange}
          icon={Workflow}
          placeholder="e.g. Alterations & Customer Styling Assistance"
        />

        <ProfileField
          label="Manufacturing Activity"
          value={data.manufacturingActivity}
          name="manufacturingActivity"
          type="select"
          options={profileOptions.yesNoOptions}
          isEditing={isEditing}
          onChange={onChange}
          icon={Factory}
        />

        <ProfileField
          label="Import Activities"
          value={data.importActivities}
          name="importActivities"
          type="select"
          options={profileOptions.yesNoOptions}
          isEditing={isEditing}
          onChange={onChange}
          icon={ArrowDownLeft}
        />

        <ProfileField
          label="Export Activities"
          value={data.exportActivities}
          name="exportActivities"
          type="select"
          options={profileOptions.yesNoOptions}
          isEditing={isEditing}
          onChange={onChange}
          icon={ArrowUpRight}
        />

        <ProfileField
          label="Environmental Impact"
          value={data.environmentalImpact}
          name="environmentalImpact"
          type="select"
          options={profileOptions.environmentalImpacts}
          isEditing={isEditing}
          onChange={onChange}
          icon={Leaf}
          badge={
            <Badge
              variant={
                data.environmentalImpact === 'High'
                  ? 'High'
                  : data.environmentalImpact === 'Low'
                  ? 'Low'
                  : 'Medium'
              }
              size="xs"
            >
              {data.environmentalImpact}
            </Badge>
          }
        />

        <ProfileField
          label="Operating Status"
          value={data.operatingStatus}
          name="operatingStatus"
          type="select"
          options={profileOptions.operatingStatuses}
          isEditing={isEditing}
          onChange={onChange}
          icon={Activity}
          badge={
            <Badge variant="Active" size="xs" withDot>
              {data.operatingStatus}
            </Badge>
          }
        />
      </div>
    </div>
  );
}