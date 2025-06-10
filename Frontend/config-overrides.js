module.exports = function override(config, env) {
  // Disable source maps for problematic packages
  config.ignoreWarnings = [
    { module: /node_modules\/@urql\/core/ },
    { module: /node_modules\/@0no-co\/graphql.web/ }
  ];

  // Disable source maps for node_modules
  if (config.devtool) {
    config.devtool = false;
  }

  return config;
}; 