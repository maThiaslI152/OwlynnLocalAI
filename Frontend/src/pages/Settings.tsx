import React from 'react';
import {
  Box,
  Paper,
  Typography,
  TextField,
  Slider,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Button,
} from '@mui/material';

const Settings: React.FC = () => {
  const [model, setModel] = React.useState('Qwen3-14B');
  const [temperature, setTemperature] = React.useState(0.65);
  const [maxTokens, setMaxTokens] = React.useState(8096);

  const handleSave = () => {
    // TODO: Implement settings save functionality
    console.log('Saving settings:', { model, temperature, maxTokens });
  };

  return (
    <Box sx={{ maxWidth: 600, mx: 'auto', mt: 4 }}>
      <Paper sx={{ p: 3 }}>
        <Typography variant="h5" gutterBottom>
          AI Model Settings
        </Typography>

        <FormControl fullWidth sx={{ mb: 3 }}>
          <InputLabel>Model</InputLabel>
          <Select
            value={model}
            label="Model"
            onChange={(e) => setModel(e.target.value)}
          >
            <MenuItem value="Qwen3-14B">Qwen3-14B</MenuItem>
            {/* Add more models as needed */}
          </Select>
        </FormControl>

        <Box sx={{ mb: 3 }}>
          <Typography gutterBottom>Temperature: {temperature}</Typography>
          <Slider
            value={temperature}
            onChange={(_, value) => setTemperature(value as number)}
            min={0}
            max={1}
            step={0.01}
            marks={[
              { value: 0, label: '0' },
              { value: 0.5, label: '0.5' },
              { value: 1, label: '1' },
            ]}
          />
        </Box>

        <TextField
          fullWidth
          label="Max Tokens"
          type="number"
          value={maxTokens}
          onChange={(e) => setMaxTokens(Number(e.target.value))}
          sx={{ mb: 3 }}
        />

        <Button
          variant="contained"
          color="primary"
          onClick={handleSave}
          fullWidth
        >
          Save Settings
        </Button>
      </Paper>
    </Box>
  );
};

export default Settings; 