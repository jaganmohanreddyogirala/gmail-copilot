import { useState, useEffect } from 'react';
import type { UserStyleMemory } from '../types/email';
import { api } from '../api/client';

export function UserStyleManager() {
  const [style, setStyle] = useState<UserStyleMemory>({
    tone: 'Professional, direct, and concise.',
    greeting_template: 'Hi {name},',
    signoff_template: 'Best regards,\nJagan',
    custom_rules: [
      'Prefer concise replies under 4 sentences.',
      'Never send passwords or API keys in text.',
    ],
  });

  const [newRule, setNewRule] = useState<string>('');
  const [loading, setLoading] = useState<boolean>(false);
  const [savedStatus, setSavedStatus] = useState<boolean>(false);

  useEffect(() => {
    const loadStyle = async () => {
      try {
        const data = await api.getUserStyle();
        if (data && data.tone) {
          setStyle(data);
        }
      } catch (err) {
        console.warn('Style memory load error:', err);
      }
    };
    loadStyle();
  }, []);

  const handleSave = async () => {
    setLoading(true);
    try {
      await api.updateUserStyle(style);
      setSavedStatus(true);
      setTimeout(() => setSavedStatus(false), 3000);
    } catch (err: any) {
      alert(`Save error: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  const handleAddRule = () => {
    if (!newRule.trim()) return;
    setStyle((prev) => ({
      ...prev,
      custom_rules: [...prev.custom_rules, newRule.trim()],
    }));
    setNewRule('');
  };

  const handleRemoveRule = (index: number) => {
    setStyle((prev) => ({
      ...prev,
      custom_rules: prev.custom_rules.filter((_, i) => i !== index),
    }));
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem', maxWidth: '800px', margin: '0 auto' }}>
      <div className="card">
        <div className="card-header">
          <div>
            <h2 className="card-title">
              <span>🎨</span> Writing Style
            </h2>
            <p className="card-subtitle">Customize how Gmail Copilot writes email response drafts</p>
          </div>
          {savedStatus && <span className="badge badge-gmail">Saved Successfully</span>}
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
          {/* Tone Selector */}
          <div>
            <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, color: 'var(--text-main)', marginBottom: '0.4rem' }}>
              Writing Tone
            </label>
            <div style={{ display: 'flex', gap: '0.5rem' }}>
              {['Professional, direct, and concise.', 'Friendly, approachable, and helpful.', 'Formal, structured, and detailed.'].map((t) => (
                <button
                  key={t}
                  type="button"
                  className={`filter-tab ${style.tone === t ? 'active' : ''}`}
                  onClick={() => setStyle({ ...style, tone: t })}
                  style={{ padding: '0.5rem 0.85rem' }}
                >
                  {t.split(',')[0]}
                </button>
              ))}
            </div>
          </div>

          {/* Greeting Template */}
          <div>
            <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, color: 'var(--text-main)', marginBottom: '0.4rem' }}>
              Default Greeting
            </label>
            <div className="search-input-box" style={{ width: '100%' }}>
              <input
                type="text"
                value={style.greeting_template}
                onChange={(e) => setStyle({ ...style, greeting_template: e.target.value })}
                placeholder="Hi {name},"
              />
            </div>
          </div>

          {/* Signoff Template */}
          <div>
            <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, color: 'var(--text-main)', marginBottom: '0.4rem' }}>
              Default Sign-off
            </label>
            <textarea
              value={style.signoff_template}
              onChange={(e) => setStyle({ ...style, signoff_template: e.target.value })}
              rows={3}
              style={{
                width: '100%',
                background: 'var(--bg-surface)',
                border: '1px solid var(--border-color)',
                borderRadius: 'var(--radius-sm)',
                padding: '0.65rem 0.85rem',
                fontSize: '0.85rem',
                color: 'var(--text-main)',
                fontFamily: 'inherit',
                outline: 'none',
              }}
            />
          </div>

          {/* Custom Writing Rules */}
          <div>
            <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, color: 'var(--text-main)', marginBottom: '0.4rem' }}>
              Custom Preferences & Rules
            </label>
            <div style={{ display: 'flex', gap: '0.5rem', marginBottom: '0.75rem' }}>
              <div className="search-input-box" style={{ flex: 1 }}>
                <input
                  type="text"
                  placeholder="e.g. Keep responses under 4 sentences."
                  value={newRule}
                  onChange={(e) => setNewRule(e.target.value)}
                  onKeyDown={(e) => e.key === 'Enter' && handleAddRule()}
                />
              </div>
              <button className="btn btn-secondary" onClick={handleAddRule}>
                Add Rule
              </button>
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.4rem' }}>
              {style.custom_rules.map((rule, idx) => (
                <div
                  key={idx}
                  style={{
                    background: 'var(--bg-subtle)',
                    border: '1px solid var(--border-subtle)',
                    borderRadius: 'var(--radius-sm)',
                    padding: '0.5rem 0.75rem',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',

                    fontSize: '0.825rem',
                  }}
                >
                  <span>{rule}</span>
                  <button
                    style={{ border: 'none', background: 'transparent', cursor: 'pointer', color: 'var(--text-muted)' }}
                    onClick={() => handleRemoveRule(idx)}
                  >
                    ✕
                  </button>
                </div>
              ))}
            </div>
          </div>

          <div style={{ display: 'flex', justifyContent: 'flex-end', marginTop: '0.5rem' }}>
            <button className="btn btn-primary" onClick={handleSave} disabled={loading}>
              {loading ? 'Saving...' : 'Save Preferences'}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
