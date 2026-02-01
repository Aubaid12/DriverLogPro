import React, { useState } from 'react';

const TripForm = ({ onSubmit, isLoading }) => {
    const [formData, setFormData] = useState({
        current_location: 'Green Bay, WI',
        pickup_location: 'Chicago, IL',
        dropoff_location: 'St. Louis, MO',
        cycle_used: '0'
    });

    const handleChange = (e) => {
        setFormData({
            ...formData,
            [e.target.name]: e.target.value
        });
    };

    const handleSubmit = (e) => {
        e.preventDefault();
        onSubmit(formData);
    };

    return (
        <form onSubmit={handleSubmit} className="card">
            <div className="input-group">
                <label>Current Location</label>
                <input
                    type="text"
                    name="current_location"
                    value={formData.current_location}
                    onChange={handleChange}
                    required
                    placeholder="City, State"
                />
            </div>

            <div className="input-group">
                <label>Pickup Location</label>
                <input
                    type="text"
                    name="pickup_location"
                    value={formData.pickup_location}
                    onChange={handleChange}
                    required
                    placeholder="City, State"
                />
            </div>

            <div className="input-group">
                <label>Dropoff Location</label>
                <input
                    type="text"
                    name="dropoff_location"
                    value={formData.dropoff_location}
                    onChange={handleChange}
                    required
                    placeholder="City, State"
                />
            </div>

            <div className="input-group">
                <label>Current Cycle Used (Hours)</label>
                <input
                    type="number"
                    name="cycle_used"
                    value={formData.cycle_used}
                    onChange={handleChange}
                    min="0"
                    step="0.1"
                    placeholder="0.0"
                />
            </div>

            <button type="submit" disabled={isLoading}>
                {isLoading ? 'Generating Plan...' : 'Generate Trip Plan'}
            </button>
        </form>
    );
};

export default TripForm;
