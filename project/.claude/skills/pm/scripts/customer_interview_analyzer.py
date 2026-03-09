#!/usr/bin/env python3
"""
客户访谈分析器
从用户访谈中提取痛点、需求、模式和机会

功能：
- 痛点提取与严重程度评估
- 需求/功能请求识别
- Jobs-to-be-done 模式识别
- 情感分析
- 关键主题和引用提取
- 竞品提及分析
"""

import re
import sys
from typing import Dict, List, Tuple, Set
from collections import Counter, defaultdict
import json

class InterviewAnalyzer:
    """分析客户访谈，提取洞察和模式"""

    def __init__(self):
        self.pain_indicators = [
            'frustrat', 'annoy', 'difficult', 'hard', 'confus', 'slow',
            'problem', 'issue', 'struggle', 'challeng', 'pain', 'waste',
            'manual', 'repetitive', 'tedious', 'boring', 'time-consuming',
            'complicated', 'complex', 'unclear', 'wish', 'need', 'want'
        ]

        self.delight_indicators = [
            'love', 'great', 'awesome', 'amazing', 'perfect', 'easy',
            'simple', 'quick', 'fast', 'helpful', 'useful', 'valuable',
            'save', 'efficient', 'convenient', 'intuitive', 'clear'
        ]

        self.request_indicators = [
            'would be nice', 'wish', 'hope', 'want', 'need', 'should',
            'could', 'would love', 'if only', 'it would help', 'suggest',
            'recommend', 'idea', 'what if', 'have you considered'
        ]

        self.jtbd_patterns = [
            r'when i\s+(.+?),\s+i want to\s+(.+?)\s+so that\s+(.+)',
            r'i need to\s+(.+?)\s+because\s+(.+)',
            r'my goal is to\s+(.+)',
            r'i\'m trying to\s+(.+)',
            r'i use \w+ to\s+(.+)',
            r'helps me\s+(.+)',
        ]

    def analyze_interview(self, text: str) -> Dict:
        """分析单个访谈记录"""
        text_lower = text.lower()
        sentences = self._split_sentences(text)

        analysis = {
            'pain_points': self._extract_pain_points(sentences),
            'delights': self._extract_delights(sentences),
            'feature_requests': self._extract_requests(sentences),
            'jobs_to_be_done': self._extract_jtbd(text_lower),
            'sentiment_score': self._calculate_sentiment(text_lower),
            'key_themes': self._extract_themes(text_lower),
            'quotes': self._extract_key_quotes(sentences),
            'metrics_mentioned': self._extract_metrics(text),
            'competitors_mentioned': self._extract_competitors(text)
        }

        return analysis

    def _split_sentences(self, text: str) -> List[str]:
        """拆分句子"""
        sentences = re.split(r'[.!?]+', text)
        return [s.strip() for s in sentences if s.strip()]

    def _extract_pain_points(self, sentences: List[str]) -> List[Dict]:
        """提取痛点"""
        pain_points = []

        for sentence in sentences:
            sentence_lower = sentence.lower()
            for indicator in self.pain_indicators:
                if indicator in sentence_lower:
                    pain_points.append({
                        'quote': sentence,
                        'indicator': indicator,
                        'severity': self._assess_severity(sentence_lower)
                    })
                    break

        return pain_points[:10]

    def _extract_delights(self, sentences: List[str]) -> List[Dict]:
        """提取正面反馈"""
        delights = []

        for sentence in sentences:
            sentence_lower = sentence.lower()
            for indicator in self.delight_indicators:
                if indicator in sentence_lower:
                    delights.append({
                        'quote': sentence,
                        'indicator': indicator,
                        'strength': self._assess_strength(sentence_lower)
                    })
                    break

        return delights[:10]

    def _extract_requests(self, sentences: List[str]) -> List[Dict]:
        """提取功能需求"""
        requests = []

        for sentence in sentences:
            sentence_lower = sentence.lower()
            for indicator in self.request_indicators:
                if indicator in sentence_lower:
                    requests.append({
                        'quote': sentence,
                        'type': self._classify_request(sentence_lower),
                        'priority': self._assess_request_priority(sentence_lower)
                    })
                    break

        return requests[:10]

    def _extract_jtbd(self, text: str) -> List[Dict]:
        """提取 Jobs to Be Done 模式"""
        jobs = []

        for pattern in self.jtbd_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                if isinstance(match, tuple):
                    job = ' → '.join(match)
                else:
                    job = match

                jobs.append({
                    'job': job,
                    'pattern': pattern
                })

        return jobs[:5]

    def _calculate_sentiment(self, text: str) -> Dict:
        """计算整体情感"""
        positive_count = sum(1 for ind in self.delight_indicators if ind in text)
        negative_count = sum(1 for ind in self.pain_indicators if ind in text)

        total = positive_count + negative_count
        if total == 0:
            sentiment_score = 0
        else:
            sentiment_score = (positive_count - negative_count) / total

        if sentiment_score > 0.3:
            sentiment_label = 'positive'
        elif sentiment_score < -0.3:
            sentiment_label = 'negative'
        else:
            sentiment_label = 'neutral'

        return {
            'score': round(sentiment_score, 2),
            'label': sentiment_label,
            'positive_signals': positive_count,
            'negative_signals': negative_count
        }

    def _extract_themes(self, text: str) -> List[str]:
        """提取关键主题"""
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at',
                     'to', 'for', 'of', 'with', 'by', 'from', 'as', 'is',
                     'was', 'are', 'were', 'been', 'be', 'have', 'has',
                     'had', 'do', 'does', 'did', 'will', 'would', 'could',
                     'should', 'may', 'might', 'must', 'can', 'shall',
                     'it', 'i', 'you', 'we', 'they', 'them', 'their'}

        words = re.findall(r'\b[a-z]{4,}\b', text)
        meaningful_words = [w for w in words if w not in stop_words]

        word_freq = Counter(meaningful_words)
        themes = [word for word, count in word_freq.most_common(10) if count >= 3]

        return themes

    def _extract_key_quotes(self, sentences: List[str]) -> List[str]:
        """提取关键引用"""
        scored_sentences = []

        for sentence in sentences:
            if len(sentence) < 20 or len(sentence) > 200:
                continue

            score = 0
            sentence_lower = sentence.lower()

            if any(ind in sentence_lower for ind in self.pain_indicators):
                score += 2
            if any(ind in sentence_lower for ind in self.request_indicators):
                score += 2
            if 'because' in sentence_lower:
                score += 1
            if 'but' in sentence_lower:
                score += 1
            if '?' in sentence:
                score += 1

            if score > 0:
                scored_sentences.append((score, sentence))

        scored_sentences.sort(reverse=True)
        return [s[1] for s in scored_sentences[:5]]

    def _extract_metrics(self, text: str) -> List[str]:
        """提取提及的指标"""
        metrics = []

        percentages = re.findall(r'\d+%', text)
        metrics.extend(percentages)

        time_metrics = re.findall(r'\d+\s*(?:hours?|minutes?|days?|weeks?|months?)', text, re.IGNORECASE)
        metrics.extend(time_metrics)

        money_metrics = re.findall(r'\$[\d,]+', text)
        metrics.extend(money_metrics)

        number_contexts = re.findall(r'(\d+)\s+(\w+)', text)
        for num, context in number_contexts:
            if context.lower() not in ['the', 'a', 'an', 'and', 'or', 'of']:
                metrics.append(f"{num} {context}")

        return list(set(metrics))[:10]

    def _extract_competitors(self, text: str) -> List[str]:
        """提取竞品提及"""
        competitor_patterns = [
            r'(?:use|used|using|tried|trying|switch from|switched from|instead of)\s+(\w+)',
            r'(\w+)\s+(?:is better|works better|is easier)',
            r'compared to\s+(\w+)',
            r'like\s+(\w+)',
            r'similar to\s+(\w+)',
        ]

        competitors = set()
        for pattern in competitor_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            competitors.update(matches)

        common_words = {'this', 'that', 'it', 'them', 'other', 'another', 'something'}
        competitors = [c for c in competitors if c.lower() not in common_words and len(c) > 2]

        return list(competitors)[:5]

    def _assess_severity(self, text: str) -> str:
        """评估痛点严重程度"""
        if any(word in text for word in ['very', 'extremely', 'really', 'totally', 'completely']):
            return 'high'
        elif any(word in text for word in ['somewhat', 'bit', 'little', 'slightly']):
            return 'low'
        return 'medium'

    def _assess_strength(self, text: str) -> str:
        """评估正面反馈强度"""
        if any(word in text for word in ['absolutely', 'definitely', 'really', 'very']):
            return 'strong'
        return 'moderate'

    def _classify_request(self, text: str) -> str:
        """分类需求类型"""
        if any(word in text for word in ['ui', 'design', 'look', 'color', 'layout']):
            return 'ui_improvement'
        elif any(word in text for word in ['feature', 'add', 'new', 'build']):
            return 'new_feature'
        elif any(word in text for word in ['fix', 'bug', 'broken', 'work']):
            return 'bug_fix'
        elif any(word in text for word in ['faster', 'slow', 'performance', 'speed']):
            return 'performance'
        return 'general'

    def _assess_request_priority(self, text: str) -> str:
        """评估需求优先级"""
        if any(word in text for word in ['critical', 'urgent', 'asap', 'immediately', 'blocking']):
            return 'critical'
        elif any(word in text for word in ['need', 'important', 'should', 'must']):
            return 'high'
        elif any(word in text for word in ['nice', 'would', 'could', 'maybe']):
            return 'low'
        return 'medium'

def format_single_interview(analysis: Dict) -> str:
    """格式化单个访谈分析结果"""
    output = ["=" * 60]
    output.append("客户访谈分析结果")
    output.append("=" * 60)

    sentiment = analysis['sentiment_score']
    sentiment_labels = {
        'positive': '正面',
        'negative': '负面',
        'neutral': '中性'
    }
    label = sentiment_labels.get(sentiment['label'], sentiment['label'])
    output.append(f"\n📊 整体情感: {label}")
    output.append(f"   评分: {sentiment['score']}")
    output.append(f"   正面信号: {sentiment['positive_signals']}")
    output.append(f"   负面信号: {sentiment['negative_signals']}")

    if analysis['pain_points']:
        severity_labels = {'high': '高', 'medium': '中', 'low': '低'}
        output.append("\n🔥 痛点识别:")
        for i, pain in enumerate(analysis['pain_points'][:5], 1):
            severity = severity_labels.get(pain['severity'], pain['severity'])
            output.append(f"\n{i}. [{severity}] {pain['quote'][:100]}...")

    if analysis['feature_requests']:
        type_labels = {
            'ui_improvement': 'UI 改进',
            'new_feature': '新功能',
            'bug_fix': 'Bug 修复',
            'performance': '性能优化',
            'general': '一般建议'
        }
        priority_labels = {'critical': '紧急', 'high': '高', 'medium': '中', 'low': '低'}
        output.append("\n💡 功能需求:")
        for i, req in enumerate(analysis['feature_requests'][:5], 1):
            req_type = type_labels.get(req['type'], req['type'])
            priority = priority_labels.get(req['priority'], req['priority'])
            output.append(f"\n{i}. [{req_type}] 优先级: {priority}")
            output.append(f"   \"{req['quote'][:100]}...\"")

    if analysis['jobs_to_be_done']:
        output.append("\n🎯 核心 Jobs to Be Done:")
        for i, job in enumerate(analysis['jobs_to_be_done'], 1):
            output.append(f"{i}. {job['job']}")

    if analysis['key_themes']:
        output.append("\n🏷️ 关键主题:")
        output.append(", ".join(analysis['key_themes']))

    if analysis['quotes']:
        output.append("\n💬 关键引用:")
        for i, quote in enumerate(analysis['quotes'][:3], 1):
            output.append(f'{i}. "{quote}"')

    if analysis['metrics_mentioned']:
        output.append("\n📈 提及的指标:")
        output.append(", ".join(analysis['metrics_mentioned']))

    if analysis['competitors_mentioned']:
        output.append("\n🏢 提及的竞品:")
        output.append(", ".join(analysis['competitors_mentioned']))

    return "\n".join(output)

def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("用法: python customer_interview_analyzer.py <访谈记录文件.txt> [json]")
        print("\n此工具可从客户访谈记录中提取:")
        print("  - 痛点和挫折")
        print("  - 功能需求和建议")
        print("  - Jobs to Be Done (待完成工作)")
        print("  - 情感分析")
        print("  - 关键主题和引用")
        print("\n示例:")
        print("  python customer_interview_analyzer.py interview.txt")
        print("  python customer_interview_analyzer.py interview.txt json  # 输出 JSON 格式")
        sys.exit(1)

    with open(sys.argv[1], 'r', encoding='utf-8') as f:
        interview_text = f.read()

    analyzer = InterviewAnalyzer()
    analysis = analyzer.analyze_interview(interview_text)

    if len(sys.argv) > 2 and sys.argv[2] == 'json':
        print(json.dumps(analysis, indent=2, ensure_ascii=False))
    else:
        print(format_single_interview(analysis))

if __name__ == "__main__":
    main()
