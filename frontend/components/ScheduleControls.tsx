'use client';

import { useState } from 'react';
import { format, addHours, addDays } from 'date-fns';
import { Clock, Calendar } from 'lucide-react';

interface ScheduleControlsProps {
  onSchedule: (date: Date) => void;
  scheduling?: boolean;
}

export default function ScheduleControls({ onSchedule, scheduling }: ScheduleControlsProps) {
  const [selectedDate, setSelectedDate] = useState<string>(
    format(addHours(new Date(), 1), "yyyy-MM-dd'T'HH:mm")
  );

  const quickOptions = [
    { label: '1 hour', date: addHours(new Date(), 1) },
    { label: '3 hours', date: addHours(new Date(), 3) },
    { label: '6 hours', date: addHours(new Date(), 6) },
    { label: 'Tomorrow', date: addDays(new Date(), 1) },
  ];

  const handleQuickSelect = (date: Date) => {
    setSelectedDate(format(date, "yyyy-MM-dd'T'HH:mm"));
  };

  const handleSchedule = () => {
    const date = new Date(selectedDate);
    onSchedule(date);
  };

  return (
    <div className="space-y-4">
      <h3 className="text-sm font-semibold text-gray-500 uppercase tracking-wide flex items-center gap-2">
        <Clock className="w-4 h-4" />
        Schedule Time
      </h3>

      {/* Quick Options */}
      <div className="flex flex-wrap gap-2">
        {quickOptions.map((option) => (
          <button
            key={option.label}
            onClick={() => handleQuickSelect(option.date)}
            className="px-3 py-2 bg-gray-100 hover:bg-prism-purple/10 text-gray-700 hover:text-prism-purple rounded-lg text-sm font-medium transition-colors"
          >
            {option.label}
          </button>
        ))}
      </div>

      {/* Custom Date/Time Picker */}
      <div className="flex items-center gap-3">
        <div className="flex-1">
          <input
            type="datetime-local"
            value={selectedDate}
            onChange={(e) => setSelectedDate(e.target.value)}
            min={format(new Date(), "yyyy-MM-dd'T'HH:mm")}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-prism-purple focus:border-transparent outline-none"
          />
        </div>
        <button
          onClick={handleSchedule}
          disabled={scheduling || !selectedDate}
          className="flex items-center gap-2 bg-prism-purple hover:bg-prism-purple/90 disabled:bg-gray-400 text-white font-semibold px-6 py-2 rounded-lg transition-colors"
        >
          <Calendar className="w-5 h-5" />
          Schedule
        </button>
      </div>

      <p className="text-xs text-gray-500">
        Scheduled for: {format(new Date(selectedDate), 'PPpp')}
      </p>
    </div>
  );
}
