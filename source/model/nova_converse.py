"""Provider adapter only; inherited original prompts/parsing and token budgets."""
from langchain_core.runnables import RunnableLambda
from source.generate.generate import Gemini_Generate


class NovaConverseGenerate(Gemini_Generate):
    def __init__(self, engine, settings):
        self.engine=engine;self.settings=settings;self.yaml_path=settings;self.provider='bedrock'
        self.usage=[]

    def _make_model(self, temperature=0.0, max_tokens=4096, top_p=1.0):
        def invoke(value):
            messages=value.to_messages() if hasattr(value,'to_messages') else value
            system=[];conversation=[]
            for message in messages:
                text=message.content
                if not isinstance(text,str):raise TypeError('Only text messages are used by the original agents')
                if message.type=='system':system.append({'text':text})
                else:conversation.append({'role':'assistant' if message.type=='ai' else 'user','content':[{'text':text}]})
            if not self.engine.refresh_llm():raise RuntimeError('AWS profile legalqa-w4 is not ready')
            result=self.engine.aws_client.converse(modelId=self.engine.model_id,system=system,messages=conversation,
                inferenceConfig={'temperature':temperature,'maxTokens':max_tokens})
            self.usage.append(result.get('usage',{}))
            return ''.join(p.get('text','') for p in result['output']['message']['content'])
        return RunnableLambda(invoke)
