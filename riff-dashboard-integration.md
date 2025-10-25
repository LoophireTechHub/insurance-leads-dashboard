# Insurance Leads Dashboard - Riff Integration Guide

## 🚀 Quick Setup

Your FastAPI backend is already running and provides REST API endpoints. Here's how to integrate it with your Riff dashboard.

---

## 📡 Available API Endpoints

### Base URL
```
https://your-riff-domain.com
```

### Endpoints

#### 1. **GET `/api/stats`** - Dashboard Statistics
Returns high-level metrics for display in dashboard cards.

**Response:**
```json
{
  "total_leads": 20,
  "high_priority": 7,
  "with_contacts": 19,
  "unique_companies": 13,
  "last_updated": "October 25, 2025 at 07:00 PM EST"
}
```

#### 2. **GET `/api/leads`** - All Leads Data
Returns complete list of leads with full details.

**Response:**
```json
{
  "leads": [
    {
      "Job Title": "Insurance Risk Manager",
      "Company Name": "Metropolitan Management Group",
      "Location": "Wyomissing, PA, US",
      "Days Open": "80",
      "Urgency Score": "86.84",
      "Salary Range": "nan nan-nan",
      "Job URL": "https://www.indeed.com/viewjob?jk=...",
      "Company Website": "http://www.myhorison.com",
      "Phone Number": "+62 21 75818999",
      "Leadership 1 Name": "Mike Braham",
      "Leadership 1 Title": "Chief Growth Officer",
      "Leadership 1 Email": "email_not_unlocked@domain.com"
    }
  ],
  "stats": { ... },
  "total": 20
}
```

#### 3. **GET `/api/leads/{index}`** - Single Lead
Get specific lead by array index (0-based).

**Example:** `/api/leads/0`

#### 4. **POST `/api/pipeline/trigger`** - Manual Pipeline Run
Manually trigger the leads collection pipeline.

**Response:**
```json
{
  "status": "success",
  "message": "Pipeline completed successfully",
  "output": "..."
}
```

#### 5. **GET `/api/health`** - Health Check
Check if the API is running.

---

## 🎨 React Dashboard Component

### Complete Dashboard with Tailwind CSS

```jsx
import React, { useState, useEffect } from 'react';
import { Search, TrendingUp, Users, Building2, ExternalLink, Phone, Globe, Mail, Calendar, DollarSign, MapPin, AlertCircle } from 'lucide-react';

const InsuranceLeadsDashboard = () => {
  const [leads, setLeads] = useState([]);
  const [stats, setStats] = useState({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [sortBy, setSortBy] = useState('urgency');

  // Fetch data from API
  useEffect(() => {
    fetchLeads();
  }, []);

  const fetchLeads = async () => {
    try {
      setLoading(true);
      const response = await fetch('/api/leads');
      const data = await response.json();

      setLeads(data.leads || []);
      setStats(data.stats || {});
      setError(null);
    } catch (err) {
      setError('Failed to load leads data');
      console.error('Error fetching leads:', err);
    } finally {
      setLoading(false);
    }
  };

  // Filter leads by search term
  const filteredLeads = leads.filter(lead => {
    const searchLower = searchTerm.toLowerCase();
    return (
      lead['Job Title']?.toLowerCase().includes(searchLower) ||
      lead['Company Name']?.toLowerCase().includes(searchLower) ||
      lead['Location']?.toLowerCase().includes(searchLower)
    );
  });

  // Sort leads
  const sortedLeads = [...filteredLeads].sort((a, b) => {
    switch (sortBy) {
      case 'urgency':
        return parseFloat(b['Urgency Score']) - parseFloat(a['Urgency Score']);
      case 'daysOpen':
        return parseInt(b['Days Open']) - parseInt(a['Days Open']);
      case 'salary':
        const salaryA = parseFloat(a['Salary Range']?.split('-')[0] || '0');
        const salaryB = parseFloat(b['Salary Range']?.split('-')[0] || '0');
        return salaryB - salaryA;
      default:
        return 0;
    }
  });

  // Get urgency badge color
  const getUrgencyColor = (score) => {
    const urgency = parseFloat(score);
    if (urgency >= 80) return 'bg-red-100 text-red-800 border-red-200';
    if (urgency >= 50) return 'bg-yellow-100 text-yellow-800 border-yellow-200';
    return 'bg-green-100 text-green-800 border-green-200';
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-indigo-600 mx-auto mb-4"></div>
          <p className="text-gray-600 text-lg">Loading insurance leads...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center">
        <div className="bg-white rounded-lg shadow-xl p-8 max-w-md">
          <AlertCircle className="w-16 h-16 text-red-500 mx-auto mb-4" />
          <h2 className="text-2xl font-bold text-gray-800 mb-2 text-center">Error Loading Data</h2>
          <p className="text-gray-600 text-center mb-4">{error}</p>
          <button
            onClick={fetchLeads}
            className="w-full bg-indigo-600 text-white py-2 px-4 rounded-lg hover:bg-indigo-700 transition"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 py-8 px-4">
      <div className="max-w-7xl mx-auto">

        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center justify-between mb-6">
            <div>
              <h1 className="text-4xl font-bold text-gray-900 mb-2">
                🎯 Insurance Leads Dashboard
              </h1>
              <p className="text-gray-600">
                Real-time commercial insurance job opportunities with contact data
              </p>
            </div>
            <button
              onClick={fetchLeads}
              className="bg-indigo-600 text-white px-6 py-3 rounded-lg hover:bg-indigo-700 transition font-semibold shadow-lg"
            >
              Refresh Data
            </button>
          </div>

          {/* Stats Cards */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
            <div className="bg-white rounded-xl shadow-lg p-6 border-l-4 border-indigo-600">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-gray-500 text-sm font-medium">Total Leads</p>
                  <p className="text-3xl font-bold text-gray-900">{stats.total_leads || 0}</p>
                </div>
                <TrendingUp className="w-12 h-12 text-indigo-600 opacity-50" />
              </div>
            </div>

            <div className="bg-white rounded-xl shadow-lg p-6 border-l-4 border-red-600">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-gray-500 text-sm font-medium">High Priority</p>
                  <p className="text-3xl font-bold text-gray-900">{stats.high_priority || 0}</p>
                </div>
                <AlertCircle className="w-12 h-12 text-red-600 opacity-50" />
              </div>
            </div>

            <div className="bg-white rounded-xl shadow-lg p-6 border-l-4 border-green-600">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-gray-500 text-sm font-medium">With Contacts</p>
                  <p className="text-3xl font-bold text-gray-900">{stats.with_contacts || 0}</p>
                </div>
                <Users className="w-12 h-12 text-green-600 opacity-50" />
              </div>
            </div>

            <div className="bg-white rounded-xl shadow-lg p-6 border-l-4 border-purple-600">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-gray-500 text-sm font-medium">Companies</p>
                  <p className="text-3xl font-bold text-gray-900">{stats.unique_companies || 0}</p>
                </div>
                <Building2 className="w-12 h-12 text-purple-600 opacity-50" />
              </div>
            </div>
          </div>

          {/* Last Updated */}
          <div className="text-center text-gray-600 text-sm mb-6">
            <Calendar className="w-4 h-4 inline mr-2" />
            Last updated: {stats.last_updated || 'Unknown'}
          </div>

          {/* Search and Filter Bar */}
          <div className="bg-white rounded-xl shadow-lg p-6 mb-8">
            <div className="flex flex-col md:flex-row gap-4">
              <div className="flex-1 relative">
                <Search className="absolute left-3 top-3 w-5 h-5 text-gray-400" />
                <input
                  type="text"
                  placeholder="Search by job title, company, or location..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                />
              </div>
              <select
                value={sortBy}
                onChange={(e) => setSortBy(e.target.value)}
                className="px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent bg-white"
              >
                <option value="urgency">Sort by Urgency</option>
                <option value="daysOpen">Sort by Days Open</option>
                <option value="salary">Sort by Salary</option>
              </select>
            </div>
            <p className="text-gray-500 text-sm mt-3">
              Showing {sortedLeads.length} of {leads.length} leads
            </p>
          </div>
        </div>

        {/* Leads Grid */}
        <div className="grid grid-cols-1 gap-6">
          {sortedLeads.map((lead, index) => (
            <div key={index} className="bg-white rounded-xl shadow-lg hover:shadow-2xl transition p-6 border border-gray-100">

              {/* Header Row */}
              <div className="flex items-start justify-between mb-4">
                <div className="flex-1">
                  <div className="flex items-center gap-3 mb-2">
                    <h3 className="text-2xl font-bold text-gray-900">
                      {lead['Job Title']}
                    </h3>
                    <span className={`px-3 py-1 rounded-full text-xs font-semibold border ${getUrgencyColor(lead['Urgency Score'])}`}>
                      {parseFloat(lead['Urgency Score']).toFixed(0)}% Urgent
                    </span>
                  </div>
                  <div className="flex items-center gap-4 text-gray-600">
                    <span className="flex items-center gap-1">
                      <Building2 className="w-4 h-4" />
                      {lead['Company Name']}
                    </span>
                    <span className="flex items-center gap-1">
                      <MapPin className="w-4 h-4" />
                      {lead['Location']}
                    </span>
                    <span className="flex items-center gap-1 text-red-600 font-semibold">
                      <Calendar className="w-4 h-4" />
                      {lead['Days Open']} days open
                    </span>
                  </div>
                </div>
              </div>

              {/* Salary and Job URL */}
              {lead['Salary Range'] && !lead['Salary Range'].includes('nan') && (
                <div className="flex items-center gap-2 mb-4 text-green-700 font-semibold">
                  <DollarSign className="w-5 h-5" />
                  {lead['Salary Range']}
                </div>
              )}

              {/* Contact Information */}
              <div className="bg-gray-50 rounded-lg p-4 mb-4">
                <h4 className="font-semibold text-gray-900 mb-3 flex items-center gap-2">
                  <Users className="w-5 h-5 text-indigo-600" />
                  Leadership Contacts
                </h4>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  {[1, 2, 3].map((num) => {
                    const name = lead[`Leadership ${num} Name`];
                    const title = lead[`Leadership ${num} Title`];
                    const email = lead[`Leadership ${num} Email`];

                    if (!name) return null;

                    return (
                      <div key={num} className="bg-white rounded-lg p-3 border border-gray-200">
                        <p className="font-semibold text-gray-900 text-sm">{name}</p>
                        <p className="text-gray-600 text-xs mb-2">{title}</p>
                        {email && (
                          <div className="flex items-center gap-1 text-indigo-600 text-xs">
                            <Mail className="w-3 h-3" />
                            {email}
                          </div>
                        )}
                      </div>
                    );
                  })}
                </div>

                {/* Company Info */}
                <div className="mt-4 pt-4 border-t border-gray-200 flex flex-wrap gap-4">
                  {lead['Company Website'] && lead['Company Website'] !== 'nan' && (
                    <a
                      href={lead['Company Website']}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="flex items-center gap-1 text-sm text-indigo-600 hover:text-indigo-800"
                    >
                      <Globe className="w-4 h-4" />
                      {lead['Company Website']}
                    </a>
                  )}
                  {lead['Phone Number'] && lead['Phone Number'] !== '' && (
                    <span className="flex items-center gap-1 text-sm text-gray-600">
                      <Phone className="w-4 h-4" />
                      {lead['Phone Number']}
                    </span>
                  )}
                </div>
              </div>

              {/* Action Button */}
              <div className="flex gap-3">
                {lead['Job URL'] && (
                  <a
                    href={lead['Job URL']}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="flex-1 bg-indigo-600 text-white py-3 px-4 rounded-lg hover:bg-indigo-700 transition font-semibold text-center flex items-center justify-center gap-2"
                  >
                    View Job Posting
                    <ExternalLink className="w-4 h-4" />
                  </a>
                )}
                <button className="px-6 py-3 border-2 border-indigo-600 text-indigo-600 rounded-lg hover:bg-indigo-50 transition font-semibold">
                  Add to CRM
                </button>
              </div>
            </div>
          ))}
        </div>

        {/* No Results */}
        {sortedLeads.length === 0 && (
          <div className="bg-white rounded-xl shadow-lg p-12 text-center">
            <Search className="w-16 h-16 text-gray-400 mx-auto mb-4" />
            <h3 className="text-xl font-semibold text-gray-900 mb-2">No leads found</h3>
            <p className="text-gray-600">Try adjusting your search criteria</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default InsuranceLeadsDashboard;
```

---

## 🔧 Deployment to Riff

### Step 1: Copy Component
1. Copy the entire React component above
2. In your Riff dashboard, create a new component file
3. Paste the code

### Step 2: Install Dependencies
If using Lucide icons (already included in most React projects):
```bash
npm install lucide-react
```

### Step 3: Configure API Base URL
Update the fetch call if your API is on a different domain:

```javascript
const response = await fetch('https://your-api-domain.com/api/leads');
```

### Step 4: Add to Your App
Import and use the component:

```jsx
import InsuranceLeadsDashboard from './InsuranceLeadsDashboard';

function App() {
  return <InsuranceLeadsDashboard />;
}
```

---

## 🎨 Customization Options

### Change Colors
Update the Tailwind classes:
- Primary color: `indigo-600` → `blue-600`, `purple-600`, etc.
- Urgency badges: Modify `getUrgencyColor()` function

### Add Features
```javascript
// Export to CSV
const exportToCSV = () => {
  const csv = leads.map(lead =>
    `${lead['Job Title']},${lead['Company Name']},${lead['Location']}`
  ).join('\n');

  const blob = new Blob([csv], { type: 'text/csv' });
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = 'insurance-leads.csv';
  a.click();
};

// Filter by urgency
const highPriorityLeads = leads.filter(lead =>
  parseFloat(lead['Urgency Score']) >= 80
);
```

---

## 📊 Alternative: Simple Table View

If you prefer a simpler table layout:

```jsx
const SimpleLeadsTable = ({ leads }) => {
  return (
    <div className="overflow-x-auto">
      <table className="min-w-full bg-white rounded-lg shadow">
        <thead className="bg-gray-100">
          <tr>
            <th className="px-6 py-3 text-left">Job Title</th>
            <th className="px-6 py-3 text-left">Company</th>
            <th className="px-6 py-3 text-left">Location</th>
            <th className="px-6 py-3 text-left">Days Open</th>
            <th className="px-6 py-3 text-left">Urgency</th>
            <th className="px-6 py-3 text-left">Action</th>
          </tr>
        </thead>
        <tbody>
          {leads.map((lead, i) => (
            <tr key={i} className="border-b hover:bg-gray-50">
              <td className="px-6 py-4 font-medium">{lead['Job Title']}</td>
              <td className="px-6 py-4">{lead['Company Name']}</td>
              <td className="px-6 py-4">{lead['Location']}</td>
              <td className="px-6 py-4 text-red-600">{lead['Days Open']}</td>
              <td className="px-6 py-4">
                <span className="px-2 py-1 rounded bg-red-100 text-red-800">
                  {parseFloat(lead['Urgency Score']).toFixed(0)}%
                </span>
              </td>
              <td className="px-6 py-4">
                <a
                  href={lead['Job URL']}
                  className="text-indigo-600 hover:underline"
                  target="_blank"
                >
                  View
                </a>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};
```

---

## 🔄 Auto-Refresh

Add automatic data refresh:

```javascript
useEffect(() => {
  fetchLeads();

  // Refresh every 5 minutes
  const interval = setInterval(fetchLeads, 5 * 60 * 1000);

  return () => clearInterval(interval);
}, []);
```

---

## 📱 Mobile Responsive

The component is already mobile-responsive with:
- Grid layouts that stack on mobile: `grid-cols-1 md:grid-cols-4`
- Flexible search bar: `flex-col md:flex-row`
- Touch-friendly buttons and cards

---

## 🚀 Next Steps

1. **Deploy FastAPI Backend** to Riff or another hosting service
2. **Copy Dashboard Component** into your Riff project
3. **Update API URL** in the fetch calls
4. **Customize styling** to match your brand
5. **Add CRM integration** for the "Add to CRM" button

---

## 🆘 Troubleshooting

### CORS Issues
If you get CORS errors, the FastAPI backend already has CORS middleware enabled. Just make sure your frontend domain is allowed.

### API Not Responding
Check `/api/health` endpoint:
```bash
curl https://your-domain.com/api/health
```

### No Data Showing
1. Check browser console for errors
2. Verify API endpoint returns data: `/api/leads`
3. Ensure backend is running: `python deploy.py start`

---

## 📞 Support

For issues or questions:
1. Check logs: `tail -f leads_pipeline.log`
2. Test API: `curl http://localhost:8000/api/stats`
3. Run pipeline manually: `python deploy.py pipeline`
