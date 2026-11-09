import {ModelConfigManager} from '../node_modules/@midscene/shared/dist/es/env/model-config-manager.mjs';
export const prescribed=Object.freeze({MIDSCENE_MODEL_AUTH_MODE:'siwc',MIDSCENE_MODEL_NAME:'gpt-6-sol',MIDSCENE_MODEL_FAMILY:'gpt-6',MIDSCENE_MODEL_REASONING_ENABLED:'true',MIDSCENE_MODEL_REASONING_EFFORT:'low',MIDSCENE_JOURNEY_EFFORT:'balance'});
export function validateReviewConfig(env){
 // Inspect names first: never read values of inherited credentials/provider options.
 for(const key of Object.keys(env))if(/^(MIDSCENE_|OPENAI_|ANTHROPIC_|AZURE_|GOOGLE_|GEMINI_|HTTP_PROXY$|HTTPS_PROXY$|ALL_PROXY$|DEBUG$)/i.test(key) && !Object.hasOwn(prescribed,key))throw Error('Review configuration conflict');
 for(const [key,value] of Object.entries(prescribed))if(env[key]!==value)throw Error('Review configuration conflict');
 const modelConfig=Object.fromEntries(Object.entries(prescribed).filter(([k])=>k!=='MIDSCENE_JOURNEY_EFFORT'));
 const manager=new ModelConfigManager(modelConfig);
 const configs=['default','insight','planning','locate'].map(role=>manager.getModelConfig(role));
 for(const c of configs)if(c.modelName!=='gpt-6-sol'||c.modelFamily!=='gpt-6'||c.authMode!=='siwc'||c.reasoningEffort!=='low'||c.reasoningEnabled!==true||c.openaiApiKey||c.openaiBaseURL||c.endpoint||c.httpProxy||c.socksProxy)throw Error('Effective review configuration rejected');
 const c=configs[1];return {modelConfig,identity:{model:c.modelName,family:c.modelFamily,auth:c.authMode,providerReasoning:c.reasoningEffort,planningEffort:env.MIDSCENE_JOURNEY_EFFORT}};
}
