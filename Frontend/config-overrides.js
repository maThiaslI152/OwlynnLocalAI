module.exports = function override(config, env) {
  // Disable source maps for problematic packages
  config.ignoreWarnings = [
    { module: /node_modules\/@urql\/core/ },
    { module: /node_modules\/@0no-co\/graphql.web/ }
  ];

  return config;
}; 