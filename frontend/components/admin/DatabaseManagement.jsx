import React, { useState, useEffect } from 'react';
import axios from 'axios';
import {
  Box,
  Button,
  Card,
  CardContent,
  CardHeader,
  Chip,
  CircularProgress,
  Divider,
  Grid,
  List,
  ListItem,
  ListItemText,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TextField,
  Typography,
} from '@mui/material';
import { CheckCircle, Error, Refresh, Warning } from '@mui/icons-material';

/**
 * Database Management Component
 * 
 * Provides an interface for viewing migration status and managing migrations.
 */
const DatabaseManagement = () => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [migrationStatus, setMigrationStatus] = useState({
    current: null,
    pending: [],
  });
  const [schemaValidation, setSchemaValidation] = useState({
    valid: true,
    differences: [],
  });
  const [newMigrationName, setNewMigrationName] = useState('');
  const [actionInProgress, setActionInProgress] = useState(false);

  // Fetch migration status on component mount
  useEffect(() => {
    fetchMigrationStatus();
  }, []);

  // Fetch migration status from API
  const fetchMigrationStatus = async () => {
    setLoading(true);
    setError(null);
    
    try {
      // In a real implementation, these would be separate API calls
      const statusResponse = await axios.get('/api/admin/database/migration-status');
      const validationResponse = await axios.get('/api/admin/database/schema-validation');
      
      setMigrationStatus(statusResponse.data);
      setSchemaValidation(validationResponse.data);
    } catch (err) {
      setError('Failed to fetch migration status: ' + (err.response?.data?.message || err.message));
    } finally {
      setLoading(false);
    }
  };

  // Create a new migration
  const createMigration = async (autogenerate = true) => {
    if (!newMigrationName.trim()) {
      setError('Migration name is required');
      return;
    }
    
    setActionInProgress(true);
    setError(null);
    
    try {
      await axios.post('/api/admin/database/migrations', {
        message: newMigrationName,
        autogenerate,
      });
      
      // Refresh migration status
      await fetchMigrationStatus();
      setNewMigrationName('');
    } catch (err) {
      setError('Failed to create migration: ' + (err.response?.data?.message || err.message));
    } finally {
      setActionInProgress(false);
    }
  };

  // Run pending migrations
  const runMigrations = async () => {
    setActionInProgress(true);
    setError(null);
    
    try {
      await axios.post('/api/admin/database/migrations/run');
      
      // Refresh migration status
      await fetchMigrationStatus();
    } catch (err) {
      setError('Failed to run migrations: ' + (err.response?.data?.message || err.message));
    } finally {
      setActionInProgress(false);
    }
  };

  // Render loading state
  if (loading && !actionInProgress) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="200px">
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Database Management
      </Typography>
      
      {error && (
        <Paper 
          elevation={0} 
          sx={{ 
            p: 2, 
            mb: 3, 
            bgcolor: 'error.light', 
            color: 'error.contrastText' 
          }}
        >
          <Box display="flex" alignItems="center">
            <Error sx={{ mr: 1 }} />
            <Typography>{error}</Typography>
          </Box>
        </Paper>
      )}
      
      <Grid container spacing={3}>
        {/* Migration Status */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardHeader 
              title="Migration Status" 
              action={
                <Button 
                  startIcon={<Refresh />} 
                  onClick={fetchMigrationStatus}
                  disabled={actionInProgress}
                >
                  Refresh
                </Button>
              }
            />
            <Divider />
            <CardContent>
              <Box mb={2}>
                <Typography variant="subtitle1">Current Revision</Typography>
                {migrationStatus.current ? (
                  <Chip 
                    label={migrationStatus.current} 
                    color="primary" 
                    sx={{ mt: 1 }}
                  />
                ) : (
                  <Typography color="text.secondary">No migrations applied</Typography>
                )}
              </Box>
              
              <Typography variant="subtitle1">Pending Migrations</Typography>
              {migrationStatus.pending.length > 0 ? (
                <List dense>
                  {migrationStatus.pending.map((migration) => (
                    <ListItem key={migration}>
                      <ListItemText primary={migration} />
                    </ListItem>
                  ))}
                </List>
              ) : (
                <Typography color="text.secondary">No pending migrations</Typography>
              )}
              
              {migrationStatus.pending.length > 0 && (
                <Button
                  variant="contained"
                  color="primary"
                  onClick={runMigrations}
                  disabled={actionInProgress}
                  sx={{ mt: 2 }}
                >
                  {actionInProgress ? <CircularProgress size={24} /> : 'Run Migrations'}
                </Button>
              )}
            </CardContent>
          </Card>
        </Grid>
        
        {/* Schema Validation */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardHeader 
              title="Schema Validation" 
              action={
                <Chip 
                  icon={schemaValidation.valid ? <CheckCircle /> : <Warning />}
                  label={schemaValidation.valid ? 'Valid' : 'Invalid'}
                  color={schemaValidation.valid ? 'success' : 'warning'}
                />
              }
            />
            <Divider />
            <CardContent>
              {schemaValidation.differences.length > 0 ? (
                <List dense>
                  {schemaValidation.differences.map((diff, index) => (
                    <ListItem key={index}>
                      <ListItemText primary={diff} />
                    </ListItem>
                  ))}
                </List>
              ) : (
                <Typography color="text.secondary">
                  Schema matches expected definition
                </Typography>
              )}
            </CardContent>
          </Card>
        </Grid>
        
        {/* Create Migration */}
        <Grid item xs={12}>
          <Card>
            <CardHeader title="Create Migration" />
            <Divider />
            <CardContent>
              <Box display="flex" alignItems="center">
                <TextField
                  label="Migration Name"
                  variant="outlined"
                  fullWidth
                  value={newMigrationName}
                  onChange={(e) => setNewMigrationName(e.target.value)}
                  disabled={actionInProgress}
                  placeholder="e.g., add_user_role_column"
                  sx={{ mr: 2 }}
                />
                <Button
                  variant="contained"
                  color="primary"
                  onClick={() => createMigration(true)}
                  disabled={!newMigrationName.trim() || actionInProgress}
                >
                  {actionInProgress ? <CircularProgress size={24} /> : 'Auto-generate'}
                </Button>
                <Button
                  variant="outlined"
                  color="primary"
                  onClick={() => createMigration(false)}
                  disabled={!newMigrationName.trim() || actionInProgress}
                  sx={{ ml: 1 }}
                >
                  Empty
                </Button>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

export default DatabaseManagement;
