"""Validate Nova's answer contract without guessing or repairing source identities."""
import json
import re


class SynthesisResponseError(ValueError):
    def __init__(self,code):
        self.code=code
        super().__init__(code)


def parse_synthesis_response(text,source_count,stop_reason=None):
    if stop_reason=='max_tokens':raise SynthesisResponseError('synthesis_truncated')
    if not isinstance(text,str):raise SynthesisResponseError('invalid_response_text')
    text=text.strip()
    if text.startswith('```'):
        text=re.sub(r'^```(?:json)?\s*','',text,flags=re.I)
        text=re.sub(r'\s*```$','',text).strip()
    try:obj=json.loads(text)
    except (ValueError,TypeError):raise SynthesisResponseError('invalid_response_json') from None
    if not isinstance(obj,dict) or not isinstance(obj.get('answer'),str) or not obj['answer'].strip():
        raise SynthesisResponseError('invalid_answer_schema')
    raw=obj.get('citations')
    if not isinstance(raw,list):raise SynthesisResponseError('invalid_citation_schema')
    keys=[]
    for value in raw:
        if type(value) is int:key=value
        elif isinstance(value,str):
            # A numeric string or explicit S-label identifies the same 1-based source.
            # Never guess an offset for 0-based keys or parse document/article numbers.
            match=re.fullmatch(r'(?:([1-9][0-9]*)|S([1-9][0-9]*)|\[S([1-9][0-9]*)\])',value.strip(),re.I)
            if not match:raise SynthesisResponseError('invalid_citation_value')
            key=int(next(group for group in match.groups() if group is not None))
        else:raise SynthesisResponseError('invalid_citation_value')
        if not 1<=key<=source_count:raise SynthesisResponseError('citation_out_of_range')
        if key not in keys:keys.append(key)
    return {'answer':obj['answer'].strip(),'citations':keys}
