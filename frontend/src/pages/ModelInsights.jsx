import { useState, useEffect } from 'react';
import api from '../api/client';

function ModelInsights() {
  const [metrics, setMetrics] = useState(null);
  const [modelInfo, setModelInfo] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const [metricsRes, infoRes] = await Promise.all([
        api.get('/models/metrics'),
        api.get('/models/info'),
      ]);
      setMetrics(metricsRes.data);
      setModelInfo(infoRes.data);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching model data:', error);
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-white text-xl">Loading model insights...</div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <h1 className="text-3xl font-bold text-white mb-8">Model Insights</h1>

      {/* Model Info */}
      {modelInfo && (
        <div className="bg-gray-800 rounded-lg p-6 border border-gray-700 mb-8">
          <h2 className="text-xl font-semibold text-white mb-4">Model Information</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <h3 className="text-gray-400 text-sm mb-2">Binary Model</h3>
              <p className="text-white">{modelInfo.binary_model?.type || 'N/A'}</p>
            </div>
            <div>
              <h3 className="text-gray-400 text-sm mb-2">Multiclass Model</h3>
              <p className="text-white">{modelInfo.multiclass_model?.type || 'N/A'}</p>
            </div>
            <div>
              <h3 className="text-gray-400 text-sm mb-2">Feature Count</h3>
              <p className="text-white">{modelInfo.feature_count || 'N/A'}</p>
            </div>
            <div>
              <h3 className="text-gray-400 text-sm mb-2">PCA Components</h3>
              <p className="text-white">{modelInfo.preprocessing?.pca?.n_components || 'N/A'}</p>
            </div>
          </div>
        </div>
      )}

      {/* Binary Model Metrics */}
      {metrics?.binary && (
        <div className="bg-gray-800 rounded-lg p-6 border border-gray-700 mb-8">
          <h2 className="text-xl font-semibold text-white mb-4">Binary Classification Metrics</h2>
          <div className="grid grid-cols-2 md:grid-cols-5 gap-4 mb-6">
            <div>
              <h3 className="text-gray-400 text-sm mb-2">Accuracy</h3>
              <p className="text-2xl font-bold text-green-400">{(metrics.binary.accuracy * 100).toFixed(1)}%</p>
            </div>
            <div>
              <h3 className="text-gray-400 text-sm mb-2">Precision</h3>
              <p className="text-2xl font-bold text-blue-400">{(metrics.binary.precision * 100).toFixed(1)}%</p>
            </div>
            <div>
              <h3 className="text-gray-400 text-sm mb-2">Recall</h3>
              <p className="text-2xl font-bold text-yellow-400">{(metrics.binary.recall * 100).toFixed(1)}%</p>
            </div>
            <div>
              <h3 className="text-gray-400 text-sm mb-2">F1 Score</h3>
              <p className="text-2xl font-bold text-purple-400">{(metrics.binary.f1_score * 100).toFixed(1)}%</p>
            </div>
            <div>
              <h3 className="text-gray-400 text-sm mb-2">ROC AUC</h3>
              <p className="text-2xl font-bold text-pink-400">{(metrics.binary.roc_auc * 100).toFixed(1)}%</p>
            </div>
          </div>

          <div className="mt-6">
            <h3 className="text-gray-300 text-sm mb-3">Confusion Matrix</h3>
            <div className="grid grid-cols-3 gap-2 max-w-md">
              <div></div>
              <div className="text-center text-gray-400 text-sm">Predicted: Benign</div>
              <div className="text-center text-gray-400 text-sm">Predicted: Attack</div>
              <div className="text-gray-400 text-sm">Actual: Benign</div>
              <div className="bg-green-900/50 p-3 rounded text-center text-white font-semibold">
                {metrics.binary.confusion_matrix.true_negative}
              </div>
              <div className="bg-red-900/50 p-3 rounded text-center text-white font-semibold">
                {metrics.binary.confusion_matrix.false_positive}
              </div>
              <div className="text-gray-400 text-sm">Actual: Attack</div>
              <div className="bg-red-900/50 p-3 rounded text-center text-white font-semibold">
                {metrics.binary.confusion_matrix.false_negative}
              </div>
              <div className="bg-green-900/50 p-3 rounded text-center text-white font-semibold">
                {metrics.binary.confusion_matrix.true_positive}
              </div>
            </div>
          </div>

          <div className="mt-6 text-sm text-gray-400">
            <p><strong>Accuracy:</strong> Overall correctness of predictions</p>
            <p><strong>Precision:</strong> Of predicted attacks, how many were actually attacks</p>
            <p><strong>Recall:</strong> Of all actual attacks, how many were detected</p>
            <p><strong>F1 Score:</strong> Harmonic mean of precision and recall</p>
            <p><strong>ROC AUC:</strong> Ability to distinguish between classes</p>
          </div>
        </div>
      )}

      {/* Multiclass Model Metrics */}
      {metrics?.multiclass && (
        <div className="bg-gray-800 rounded-lg p-6 border border-gray-700 mb-8">
          <h2 className="text-xl font-semibold text-white mb-4">Multiclass Classification Metrics</h2>
          <div className="mb-6">
            <h3 className="text-gray-300 text-lg mb-3">Overall Accuracy: {(metrics.multiclass.accuracy * 100).toFixed(1)}%</h3>
          </div>

          <div className="mb-6">
            <h3 className="text-gray-300 text-sm mb-3">Per-Class Metrics</h3>
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-700">
                <thead>
                  <tr>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-400 uppercase">Class</th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-400 uppercase">Precision</th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-400 uppercase">Recall</th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-400 uppercase">F1 Score</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-700">
                  {Object.entries(metrics.multiclass.per_class || {}).map(([class_name, class_metrics]) => (
                    <tr key={class_name}>
                      <td className="px-4 py-3 text-sm text-white">{class_name}</td>
                      <td className="px-4 py-3 text-sm text-blue-400">{(class_metrics.precision * 100).toFixed(1)}%</td>
                      <td className="px-4 py-3 text-sm text-yellow-400">{(class_metrics.recall * 100).toFixed(1)}%</td>
                      <td className="px-4 py-3 text-sm text-purple-400">{(class_metrics.f1_score * 100).toFixed(1)}%</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          <div className="mt-6">
            <h3 className="text-gray-300 text-sm mb-3">Confusion Matrix</h3>
            <div className="overflow-x-auto">
              <table className="min-w-full">
                <thead>
                  <tr>
                    <th className="px-2 py-2 text-xs text-gray-400"></th>
                    {metrics.multiclass.confusion_matrix.classes.map(cls => (
                      <th key={cls} className="px-2 py-2 text-xs text-gray-400 text-center">{cls}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {metrics.multiclass.confusion_matrix.matrix.map((row, i) => (
                    <tr key={i}>
                      <td className="px-2 py-2 text-xs text-gray-400">{metrics.multiclass.confusion_matrix.classes[i]}</td>
                      {row.map((cell, j) => (
                        <td
                          key={j}
                          className={`px-2 py-2 text-xs text-center ${
                            i === j
                              ? 'bg-green-900/50 text-green-300'
                              : cell > 0
                              ? 'bg-red-900/50 text-red-300'
                              : 'bg-gray-900/50 text-gray-500'
                          }`}
                        >
                          {cell}
                        </td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default ModelInsights;

