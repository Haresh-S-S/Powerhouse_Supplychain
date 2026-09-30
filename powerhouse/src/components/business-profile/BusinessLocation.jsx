import React from 'react';
import {
  MapPin,
  Building,
  Navigation,
  Globe2,
  Compass,
  Map
} from 'lucide-react';
import ProfileField from '../shared/ProfileField';
import { profileOptions } from '../../data/businessProfileData';

export default function BusinessLocation({ data, isEditing, onChange }) {
  return (
    <div className="bg-[#111827] rounded-2xl border border-[#1E293B] shadow-2xs p-5 sm:p-6">
      {/* Header */}
      <div className="flex items-center gap-2.5 pb-4 border-b border-slate-800">
        <div className="p-1.5 rounded-lg bg-blue-950 text-blue-400 border border-blue-800">
          <MapPin className="w-4 h-4" />
        </div>
        <div>
          <h3 className="text-base font-bold text-white leading-none">
            Business Location
          </h3>
          <p className="text-xs text-slate-400 mt-1">
            Registered location and operating address.
          </p>
        </div>
      </div>

      {/* Content grid */}
      <div className="mt-4 grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
        <div className="lg:col-span-7 divide-y divide-slate-800/60">
          <ProfileField
            label="Registered Address"
            value={data.registeredAddress}
            name="registeredAddress"
            type="textarea"
            isEditing={isEditing}
            onChange={onChange}
            icon={Building}
            placeholder="Address..."
          />

          <ProfileField
            label="City"
            value={data.city}
            name="city"
            isEditing={isEditing}
            onChange={onChange}
            icon={Navigation}
            placeholder="e.g. Tiruppur"
          />

          <ProfileField
            label="State"
            value={data.state}
            name="state"
            type="select"
            options={profileOptions.states}
            isEditing={isEditing}
            onChange={onChange}
            icon={Compass}
          />

          <ProfileField
            label="Country"
            value={data.country}
            name="country"
            isEditing={isEditing}
            onChange={onChange}
            icon={Globe2}
            placeholder="India"
          />

          <ProfileField
            label="PIN Code"
            value={data.pinCode}
            name="pinCode"
            isEditing={isEditing}
            onChange={onChange}
            icon={MapPin}
            placeholder="641604"
          />

          <ProfileField
            label="Operating Location"
            value={data.operatingLocation}
            name="operatingLocation"
            isEditing={isEditing}
            onChange={onChange}
            icon={Map}
            placeholder="Tiruppur, Tamil Nadu"
          />
        </div>

        {/* Location Graphic Card */}
        <div className="lg:col-span-5 flex flex-col items-center justify-center p-6 bg-[#141C2B] rounded-xl border border-slate-800 text-center min-h-[220px]">
          <div className="relative mb-3">
            <div className="w-16 h-16 rounded-2xl bg-blue-950 border border-blue-800 flex items-center justify-center text-blue-400 shadow-xs">
              <MapPin className="w-8 h-8" />
            </div>
          </div>
          <span className="text-xs font-bold text-white block">
            {data.city || 'Tiruppur'}, {data.state || 'Tamil Nadu'}
          </span>
          <p className="text-[11px] text-slate-400 max-w-[200px] mt-1">
            Statutory jurisdiction: {data.city || 'Tiruppur'} Municipal Corporation &amp; State Commercial Taxes.
          </p>
        </div>
      </div>
    </div>
  );
}